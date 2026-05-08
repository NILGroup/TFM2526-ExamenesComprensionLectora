from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from langgraph.graph import END, START, StateGraph

from .agents import MatchingAgents
from .dataset import load_matching_exercise
from .gemini_client import GeminiClient
from .ollama_client import OllamaClient
from .state import Item, MatchingGraphState


def _find_item(items: list[Item], item_id: str) -> Item | None:
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def _safe_resolver_pairs(
    proposed: list[tuple[str, str]],
    unresolved_questions: list[Item],
    available_answers: list[Item],
) -> dict[str, str]:
    valid_qids = {q["id"] for q in unresolved_questions}
    valid_aids = {a["id"] for a in available_answers}

    result: dict[str, str] = {}
    used_answers: set[str] = set()

    for qid, aid in proposed:
        if qid in valid_qids and aid in valid_aids and qid not in result and aid not in used_answers:
            result[qid] = aid
            used_answers.add(aid)

    remaining_answers = [a["id"] for a in available_answers if a["id"] not in used_answers]
    for q in unresolved_questions:
        qid = q["id"]
        if qid not in result and remaining_answers:
            result[qid] = remaining_answers.pop(0)

    return result


@dataclass
class MatchingAgentSystem:
    model: str = "gemma4:e4b"
    ollama_url: str = "http://localhost:11434"
    backend: str = "ollama"
    gemini_model: str = "gemini-2.5-flash-lite"
    gemini_api_key: str | None = None
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    trace: bool = False

    def _trace(self, message: str) -> None:
        if self.trace:
            print(f"[trace] {message}", flush=True)

    def __post_init__(self) -> None:
        backend = self.backend.lower().strip()
        if backend == "gemini":
            self._trace("Inicializando backend Gemini para inferencia via API.")
            self.client = GeminiClient(
                model=self.gemini_model,
                api_key=self.gemini_api_key
            )
        elif backend == "ollama":
            self._trace("Inicializando backend Ollama.")
            self.client = OllamaClient(model=self.model, base_url=self.ollama_url)
        else:
            raise ValueError("backend invalido. Usa 'ollama' o 'gemini'.")
        self.agents = MatchingAgents(self.client, tracer=self._trace if self.trace else None)
        self.graph = self._build_graph()

    def _build_graph(self):
        graph_builder = StateGraph(MatchingGraphState)

        def orchestrator_node(state: MatchingGraphState) -> dict:
            self._trace("Nodo orquestador: iniciando clasificacion de ruta.")
            try:
                out = self.agents.orchestrate(
                    state["original_questions"],
                    state["available_answers"],
                    state["exercise_instructions"],
                )
                return {"task_type": out.task_type}
            except Exception as exc:
                self._trace(f"Orchestrator error: {exc}")
                fallback_task = "A" if len(state["original_questions"]) > len(state["available_answers"]) else "B"
                return {"task_type": fallback_task, "orchestrator_error": str(exc)}

        def path_a_resolver_node(state: MatchingGraphState) -> dict:
            idx = state["current_question_index"]
            question = state["original_questions"][idx]
            self._trace(
                f"Path A - Resolver: pregunta_idx={idx} pregunta_id={question['id']} intentos={state['current_question_attempts']}"
            )
            try:
                out = self.agents.micro_resolve(
                    question=question,
                    answers=state["available_answers"],
                    previous_feedback=state.get("latest_review_feedback", ""),
                )
                return {
                    "latest_micro_candidate": {
                        "question_id": out.question_id,
                        "selected_answer_id": out.selected_answer_id,
                    }
                }
            except Exception as exc:
                self._trace(f"micro_resolve error for q={question['id']}: {exc}")
                attempts = state.get("current_question_attempts", 0) + 1
                return {
                    "latest_micro_candidate": {"question_id": question["id"], "selected_answer_id": ""},
                    "current_question_attempts": attempts,
                    "latest_review_feedback": str(exc),
                }

        def path_a_reviewer_node(state: MatchingGraphState) -> dict:
            idx = state["current_question_index"]
            question = state["original_questions"][idx]
            candidate = state["latest_micro_candidate"]
            question_id = question["id"]
            selected_id = candidate.get("selected_answer_id", "")
            self._trace(
                f"Path A - Reviewer: revisando q={question_id} con candidato a={selected_id or 'N/A'}"
            )

            selected_answer = _find_item(state["available_answers"], selected_id)
            if selected_answer is None:
                selected_answer = state["available_answers"][0]
                selected_id = selected_answer["id"]
                self._trace(
                    f"Path A - Reviewer: candidato invalido, se usa fallback a={selected_id}"
                )

            try:
                review = self.agents.micro_review(
                    question=question,
                    selected_answer=selected_answer,
                    answers=state["available_answers"],
                )
            except Exception as exc:
                self._trace(f"micro_review error for q={question_id} a={selected_id}: {exc}")
                review = SimpleNamespace(status="fail", feedback=str(exc))

            if review.status == "pass":
                matches = dict(state["current_matches"])
                matches[question_id] = selected_id
                self._trace(
                    f"Path A - Reviewer: PASS q={question_id} -> a={selected_id}. Avanza a la siguiente pregunta."
                )
                return {
                    "current_matches": matches,
                    "current_question_index": idx + 1,
                    "current_question_attempts": 0,
                    "latest_review_feedback": "",
                }

            attempts = state["current_question_attempts"] + 1
            if attempts >= 3:
                matches = dict(state["current_matches"])
                matches[question_id] = selected_id
                self._trace(
                    f"Path A - Reviewer: FAIL (max intentos). Forzando q={question_id} -> a={selected_id}."
                )
                return {
                    "current_matches": matches,
                    "current_question_index": idx + 1,
                    "current_question_attempts": 0,
                    "latest_review_feedback": review.feedback,
                }

            self._trace(
                f"Path A - Reviewer: FAIL q={question_id}. Reintento {attempts}/3."
            )
            return {
                "current_question_attempts": attempts,
                "latest_review_feedback": review.feedback,
            }

        def path_b_resolver_node(state: MatchingGraphState) -> dict:
            queue_ids = state.get("preguntas_huerfanas") or [
                q["id"] for q in state["original_questions"] if q["id"] not in state["current_matches"]
            ]
            unresolved = [
                q
                for q in state["original_questions"]
                if q["id"] in queue_ids and q["id"] not in state["current_matches"]
            ]
            if not unresolved:
                self._trace("Path B - Resolver: no hay preguntas pendientes de consenso.")
                return {}

            self._trace(
                f"Path B - Resolver: preguntas_pendientes={len(unresolved)} respuestas_disponibles={len(state['available_answers'])}"
            )

            available_by_id = {a["id"]: a for a in state["available_answers"]}
            direct_draft: dict[str, str] = {}
            direct_answer_for_question: dict[str, str] = {}
            direct_pool = dict(available_by_id)
            for question in unresolved:
                try:
                    direct_out = self.agents.path_b_q2a(question, list(direct_pool.values()))
                    aid = (direct_out.selected_answer_id or "").strip()
                except Exception as exc:
                    self._trace(f"path_b_q2a error for q={question['id']}: {exc}")
                    aid = ""
                    direct_out = SimpleNamespace(selected_answer_id="")

                qid = question["id"]
                direct_draft[qid] = aid
                if aid in direct_pool:
                    direct_answer_for_question[qid] = aid
                    direct_pool.pop(aid, None)

            inverse_draft: dict[str, str | None] = {}
            for answer in state["available_answers"]:
                try:
                    inverse_out = self.agents.path_b_a2q(answer, state["original_questions"])
                    matched_qid = (inverse_out.question_id or "").strip() or None
                except Exception as exc:
                    self._trace(f"path_b_a2q error for a={answer['id']}: {exc}")
                    matched_qid = None
                inverse_draft[answer["id"]] = matched_qid

            board = dict(state["current_matches"])
            remaining_answers = {a["id"]: a for a in state["available_answers"]}
            orphans: list[str] = []

            for question in unresolved:
                qid = question["id"]
                direct_answer_id = direct_draft.get(qid, "").strip()
                
                inverse_claims = [aid for aid, q in inverse_draft.items() if q == qid]

                if not direct_answer_id:
                    if len(inverse_claims) == 1:
                        board[qid] = inverse_claims[0]
                        remaining_answers.pop(inverse_claims[0], None)
                    elif len(inverse_claims) > 1:
                        candidate_ids = inverse_claims
                    else:
                        orphans.append(qid)
                    
                    if len(inverse_claims) != 1:
                        pass
                
                elif len(inverse_claims) == 1 and inverse_claims[0] == direct_answer_id:
                    board[qid] = direct_answer_id
                    remaining_answers.pop(direct_answer_id, None)
                    continue
                
                else:
                    candidate_ids = [direct_answer_id]
                    for aid in inverse_claims:
                        if aid not in candidate_ids:
                            candidate_ids.append(aid)

                if 'candidate_ids' in locals() and candidate_ids:
                    candidate_objs = [remaining_answers[aid] for aid in candidate_ids if aid in remaining_answers]

                    selected: dict | None = None
                    if candidate_objs:
                        if len(candidate_objs) == 1:
                            selected = candidate_objs[0]
                        else:
                            try:
                                audit = self.agents.path_b_audit_candidates(question, candidate_objs)
                                selected_id = (audit.selected_answer_id or "").strip()
                            except Exception as exc:
                                self._trace(f"path_b_audit_candidates error for q={question['id']}: {exc}")
                                selected_id = ""
                            if selected_id:
                                selected = next((cand for cand in candidate_objs if cand["id"] == selected_id), None)

                    if selected is not None:
                        board[qid] = selected["id"]
                        remaining_answers.pop(selected["id"], None)
                    else:
                        if candidate_objs:
                            fallback = candidate_objs[0]
                            board[qid] = fallback["id"]
                            remaining_answers.pop(fallback["id"], None)
                        else:
                            orphans.append(qid)
                    del candidate_ids 
                continue

            if orphans and remaining_answers:
                self._trace(f"Path B - Sweeper: Resolviendo {len(orphans)} preguntas huérfanas...")
                
                for qid in list(orphans):
                    if not remaining_answers:
                        break
                        
                    question_obj = next((q for q in unresolved if q["id"] == qid), None)
                    if not question_obj:
                        continue

                    try:
                        sweep_out = self.agents.path_b_q2a(question_obj, list(remaining_answers.values()))
                        selected_id = (sweep_out.selected_answer_id or "").strip()
                    except Exception as exc:
                        self._trace(f"path_b_q2a (sweeper) error for q={qid}: {exc}")
                        selected_id = ""

                    if selected_id in remaining_answers:
                        board[qid] = selected_id
                        remaining_answers.pop(selected_id, None)
                        orphans.remove(qid)
                    else:
                        fallback_id = list(remaining_answers.keys())[0]
                        board[qid] = fallback_id
                        remaining_answers.pop(fallback_id, None)
                        orphans.remove(qid)
                        self._trace(f"Path B - Sweeper: Asignación forzada por fallback para {qid}")

            if orphans:
                self._trace("CRÍTICO: Quedaron huérfanas sin respuestas disponibles.")

            self._trace(
                f"Path B - Resolver: tablero_parcial={len(board)} orphans={len(orphans)} respuestas_restantes={len(remaining_answers)}"
            )

            return {
                "tablero_final": board,
                "current_matches": board,
                "borrador_directo": direct_draft,
                "borrador_inverso": inverse_draft,
                "available_answers": list(remaining_answers.values()),
                "preguntas_huerfanas": orphans,
            }

        graph_builder.add_node("orchestrator", orchestrator_node)
        graph_builder.add_node("path_a_resolver", path_a_resolver_node)
        graph_builder.add_node("path_a_reviewer", path_a_reviewer_node)
        graph_builder.add_node("path_b_resolver", path_b_resolver_node)

        graph_builder.add_edge(START, "orchestrator")

        def route_by_type(state: MatchingGraphState) -> str:
            raw_route = state["task_type"] or "B"
            route = "Type_A" if raw_route == "A" else "Type_B"
            self._trace(f"Router principal: ruta seleccionada={route} (orchestrator={raw_route})")
            return route

        graph_builder.add_conditional_edges(
            "orchestrator",
            route_by_type,
            {
                "Type_A": "path_a_resolver",
                "Type_B": "path_b_resolver",
            },
        )

        graph_builder.add_edge("path_a_resolver", "path_a_reviewer")

        def route_path_a(state: MatchingGraphState) -> str:
            if state["current_question_index"] >= len(state["original_questions"]):
                self._trace("Path A: todas las preguntas resueltas. Fin.")
                return "finish"
            self._trace("Path A: continua con la siguiente pregunta.")
            return "continue"

        graph_builder.add_conditional_edges(
            "path_a_reviewer",
            route_path_a,
            {"continue": "path_a_resolver", "finish": END},
        )

        def route_path_b(state: MatchingGraphState) -> str:
            unresolved = [
                q for q in state["original_questions"] if q["id"] not in state["current_matches"]
            ]
            if not unresolved:
                self._trace("Path B: no quedan preguntas sin resolver. Fin.")
                return "finish"
            if not state["available_answers"]:
                self._trace("Path B: no quedan respuestas disponibles. Fin.")
                return "finish"
            self._trace("Path B: quedan preguntas por resolver, se continúa.")
            return "retry"

        graph_builder.add_conditional_edges(
            "path_b_resolver",
            route_path_b,
            {"retry": "path_b_resolver", "finish": END},
        )

        return graph_builder.compile()

    def solve(
        self,
        input_json_path: str | Path,
        exam_index: int = 0,
        exercise_index: int = 0,
    ) -> dict:
        self._trace(
            f"Inicio solve: input={Path(input_json_path).resolve()} exam_index={exam_index} exercise_index={exercise_index}"
        )
        questions, answers, instructions, gold, exercise_id = load_matching_exercise(
            input_json_path,
            exam_index=exam_index,
            exercise_index=exercise_index,
        )
        self._trace(
            f"Dataset cargado: exercise_id={exercise_id} preguntas={len(questions)} respuestas={len(answers)} gold={len(gold)}"
        )

        initial_state: MatchingGraphState = {
            "task_type": None,
            "exercise_instructions": instructions,
            "original_questions": questions,
            "all_answers": list(answers),
            "available_answers": list(answers),
            "current_matches": {},
            "tablero_final": {},
            "borrador_directo": {},
            "borrador_inverso": {},
            "preguntas_huerfanas": [q["id"] for q in questions],
            "current_question_index": 0,
            "current_question_attempts": 0,
            "global_iteration_count": 0,
            "flagged_questions": [],
            "latest_micro_candidate": {},
            "latest_review_feedback": "",
        }

        final_state = self.graph.invoke(initial_state)
        self._trace(
            f"Fin solve: task_type={final_state.get('task_type')} matches={len(final_state.get('current_matches', {}))}"
        )
        return {
            exercise_id: final_state.get("current_matches", {})
        }
