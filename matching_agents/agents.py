from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from .ollama_client import OllamaClient
from .schemas import (
    PathBAuditBatchOutput,
    PathBq2aOutput,
    PathBa2qOutput,
    MicroResolverOutput,
    MicroReviewerOutput,
    OrchestratorOutput,
)
from .state import Item

ORCHESTRATOR_SYSTEM = """Eres un Agente Clasificador experto en lógica de emparejamiento (Matching Tasks).
Tu objetivo es determinar la estrategia de resolución basándote en la relación entre preguntas y respuestas.

### Categorías de Tarea:
- "A" (Muchos a Pocos / Repetición): Se selecciona cuando hay más preguntas que respuestas O cuando las instrucciones indican que las respuestas pueden reutilizarse.
- "B" (Uno a Uno / Descarte): Se selecciona cuando hay más respuestas que preguntas (sobran distractores) o igual número sin posibilidad de repetición.

### Reglas de Salida:
1. Analiza primero las instrucciones.
2. Compara la cardinalidad proporcionada.
3. Devuelve EXCLUSIVAMENTE un objeto JSON. No añadas texto adicional ni explicaciones.
"""

A_RESOLVER_SYSTEM = """Eres un experto en resolución de ejercicios de comprensión lectora.
Tu tarea es analizar una única pregunta y seleccionar la respuesta correcta de un conjunto que puede tener distractores, basándote en el texto y las imágenes (si las hay).

### Pasos a seguir:
1. Evaluación de Candidatos: Compara la pregunta con CADA una de las posibles respuestas.
2. Si dos respuestas parecen correctas, elige la que sea más específica o semánticamente completa.
3. Si existe feedback de intentos previos, descarta las opciones que ya fueron invalidadas.

### Reglas Críticas:
- No inventes información. Si consideras que ninguna respuesta es adecuada, elige la que menos se contradiga con la pregunta.
- El formato de salida debe ser exclusivamente JSON.
"""

A_REVIEWER_SYSTEM = """Eres un experto en corregir ejercicios de comprensión lectora.
Debes analizar la pareja pregunta-respuesta propuesta y compararla con el resto de opciones disponibles para asegurar que no haya una mejor alternativa.

Revisa la pregunta, la respuesta seleccionada y el resto de opciones posibles asegurándote de que la respuesta elegida es la que mejor encaja.
Fíjate en que el alumno no haya caído en alguna trampa de palabras clave o se haya confundido con un distractor.
Recuerda que en estos ejercicios el emparejamiento rara vez es literal. A menudo se conectan necesidades o intereses con soluciones afines.
Tu trabajo no es juzgar si la respuesta es perfecta en el mundo real, sino determinar si es la MEJOR entre las opciones disponibles.

### Criterios de Decisión:
- **PASS**: Si la respuesta escogida es la mejor disponible.
- **FAIL**: Si la respuesta es incorrecta o si existe otra opción entre las posibles que encaja mejor.

### Instrucciones de Feedback:
- Si es FAIL: Debes explicar por qué la respuesta seleccionada no es adecuada y, si es posible, señalar cuál de las otras opciones sería mejor.
- Devuelve estrictamente un JSON.
"""

B_Q2A_SYSTEM = """Eres un experto en resolver ejercicios de comprensión lectora.
Tu objetivo es seleccionar la respuesta que mejor encaje o responda a la pregunta dada, entre un conjunto de opciones que pueden incluir distractores.

### Criterios de Selección:
1. Selecciona la respuesta que complete, defina o responda de forma más precisa a la pregunta.
2. No asumas información que no esté explícitamente en el texto.

### Reglas de Salida:
- Razona brevemente sobre por qué esa respuesta es la mejor.
- Devuelve exclusivamente JSON válido.
"""

B_A2Q_SYSTEM = """Eres un experto en resolver ejercicios de comprensión lectora.
Tu objetivo es determinar a qué pregunta pertenece una respuesta específica o identificar si se trata de un distractor.

### Protocolo de Decisión:
1. Analiza si la respuesta responde, define o completa alguna de las preguntas.
2. Si la respuesta encaja parcialmente en varias, elige la pregunta donde el encaje sea más fuerte y específico.
3. Si la respuesta es irrelevante, falsa o no tiene una conexión lógica clara con ninguna pregunta, debes clasificarla como distractor (sin asociarla con ninguna pregunta).

### Reglas de Salida:
- Si hay emparejamiento: `question_id` debe ser el ID exacto de la pregunta.
- Si es un distractor: `question_id` debe ser `null`.
- El razonamiento debe explicar brevemente por qué responde a una pregunta o por qué se considera un distractor.
- Devuelve exclusivamente JSON válido.
"""

B_AUDIT_SYSTEM = """Eres un experto en resolver ejercicios de comprensión lectora. Tu especialidad es la resolución de ambigüedades en ejercicios de emparejamiento complejos.
Tu tarea es resolver un conflicto de opciones evaluando SIMULTÁNEAMENTE múltiples respuestas candidatas para una misma pregunta.

### Reglas de Arbitraje:
1. Compara la pregunta con las posibles respuestas para ver cuál es la que mejor encaja o responde a la pregunta.
2. Identifica si alguna opción ha sido diseñada para confundir.
3. Penaliza los distractores o respuestas genéricas si hay una opción más específica.

Debes generar un razonamiento breve explicando por qué has elegido esa opción.
Devuelve exclusivamente un JSON válido con la decisión final.
"""

@dataclass
class MatchingAgents:
    llm: OllamaClient
    tracer: Callable[[str], None] | None = None

    def _trace(self, message: str) -> None:
        if self.tracer is not None:
            self.tracer(message)

    @staticmethod
    def _item_repr(item: Item) -> str:
        label = str(item.get("id", "")).strip()
        text = str(item.get("text", "")).strip()
        has_image = bool(item.get("image_b64"))

        if text and has_image:
            content = f"{text} [imagen]"
        elif text:
            content = text
        elif has_image:
            content = "[imagen]"
        else:
            content = "[sin contenido]"

        return f"{label}) {content}"

    def orchestrate(
        self,
        questions: list[Item],
        answers: list[Item],
        instructions: str,
    ) -> OrchestratorOutput:
        self._trace(
            f"[orchestrator] Clasificando tarea con {len(questions)} preguntas y {len(answers)} respuestas."
        )
        user_prompt = (
            "Analiza el enunciado y clasifícalo:\n "
            f"- Instrucciones: {instructions or 'No proporcionadas'}\n"
            f"- Cantidad de preguntas: {len(questions)}\n"
            f"- Cantidad de respuestas: {len(answers)}\n"
            'Devuelve solo JSON con task_type igual a "A" o "B".'
        )
        out = self.llm.chat_structured(
            system_prompt=ORCHESTRATOR_SYSTEM,
            user_prompt=user_prompt,
            response_model=OrchestratorOutput,
        )
        self._trace(f"[orchestrator] task_type={out.task_type}")
        return out

    def micro_resolve(
        self,
        question: Item,
        answers: list[Item],
        previous_feedback: str,
    ) -> MicroResolverOutput:
        self._trace(
            f"[micro-resolver] Resolviendo pregunta {question['id']} (pool={len(answers)} respuestas)."
        )
        answer_lines = "\n".join(self._item_repr(a) for a in answers)
        user_prompt = (
            "Empareja la siguiente pregunta con la respuesta más adecuada:\n"
            f"{self._item_repr(question)}\n\n"
            "- Posibles respuestas:\n"
            f"{answer_lines}\n\n"
            f"Feedback del revisor: {previous_feedback or 'ninguno'}\n"
            "Devuelve un JSON con question_id, selected_answer_id y reasoning."
        )

        images = [question["image_b64"]] if question.get("image_b64") else []
        images.extend(a["image_b64"] for a in answers if a.get("image_b64"))

        out = self.llm.chat_structured(
            system_prompt=A_RESOLVER_SYSTEM,
            user_prompt=user_prompt,
            response_model=MicroResolverOutput,
            images=images,
        )
        self._trace(
            f"[micro-resolver] Candidato: q={out.question_id} -> a={out.selected_answer_id}"
        )
        return out

    def micro_review(
        self,
        question: Item,
        selected_answer: Item,
        answers: list[Item],
    ) -> MicroReviewerOutput:
        self._trace(
            f"[micro-reviewer] Revisando pregunta {question['id']} con respuesta {selected_answer['id']}."
        )
        other_answers = [a for a in answers if a.get("id") != selected_answer.get("id")]
        answer_lines = "\n".join(self._item_repr(a) for a in other_answers)
        user_prompt = (
            "Comprueba si la respuesta seleccionada es la mejor opción para la pregunta dada, comparándola con el resto de respuestas posibles.\n"
            "- Pregunta:\n"
            f"{self._item_repr(question)}\n\n"
            "- Respuesta seleccionada:\n"
            f"{self._item_repr(selected_answer)}\n\n"
            "- Otras Posibles respuestas:\n"
            f"{answer_lines}\n\n"
            "Devuelve JSON con status ('pass'|'fail') y feedback."
        )

        images = []
        def _push_img(img_b64: str | None) -> None:
            if not img_b64:
                return
            if img_b64 not in images:
                images.append(img_b64)

        _push_img(question.get("image_b64"))
        _push_img(selected_answer.get("image_b64"))
        for a in other_answers:
            _push_img(a.get("image_b64"))

        out = self.llm.chat_structured(
            system_prompt=A_REVIEWER_SYSTEM,
            user_prompt=user_prompt,
            response_model=MicroReviewerOutput,
            images=images,
        )
        self._trace(f"[micro-reviewer] status={out.status} feedback={out.feedback}")
        return out

    def path_b_q2a(
        self,
        question: Item,
        answers: list[Item],
    ) -> PathBq2aOutput:
        self._trace(
            f"[path-b-q2a] Resolviendo pregunta {question['id']} con {len(answers)} respuestas disponibles."
        )
        answer_lines = "\n".join(self._item_repr(a) for a in answers)
        user_prompt = (
            "Pregunta:\n"
            f"{self._item_repr(question)}\n\n"
            "Respuestas disponibles:\n"
            f"{answer_lines}\n\n"
            "Selecciona la mejor respuesta para la pregunta planteada."
        )
        images = [question["image_b64"]] if question.get("image_b64") else []
        images.extend(a["image_b64"] for a in answers if a.get("image_b64"))
        out = self.llm.chat_structured(
            system_prompt=B_Q2A_SYSTEM,
            user_prompt=user_prompt,
            response_model=PathBq2aOutput,
            images=images,
        )
        self._trace(
            f"[path-b-q2a] q={out.question_id} -> a={out.selected_answer_id}"
        )
        return out

    def path_b_a2q(
        self,
        answer: Item,
        questions: list[Item],
    ) -> PathBa2qOutput:
        self._trace(
            f"[path-b-a2q] Asociando respuesta {answer['id']} con una de las {len(questions)} preguntas."
        )
        question_lines = "\n".join(self._item_repr(q) for q in questions)
        user_prompt = (
            "Respuesta de referencia:\n"
            f"{self._item_repr(answer)}\n\n"
            "Preguntas originales:\n"
            f"{question_lines}\n\n"
            "Determina a qué pregunta pertenece esta respuesta. Si es un distractor que no encaja en ninguna, devuelve question_id como null."
        )
        images = [answer["image_b64"]] if answer.get("image_b64") else []
        images.extend(q["image_b64"] for q in questions if q.get("image_b64"))
        out = self.llm.chat_structured(
            system_prompt=B_A2Q_SYSTEM,
            user_prompt=user_prompt,
            response_model=PathBa2qOutput,
            images=images,
        )
        self._trace(
            f"[path-b-a2q] a={out.answer_id} -> q={out.question_id or 'Ninguna'}"
        )
        return out

    def path_b_audit_candidates(
        self,
        question: Item,
        answers: list[Item],
    ) -> PathBAuditBatchOutput:
        self._trace(
            f"[path-b-audit-batch] Auditando q={question['id']} con {len(answers)} candidatas a la vez."
        )
        answer_lines = "\n".join(self._item_repr(a) for a in answers)
        user_prompt = (
            "Pregunta:\n"
            f"{self._item_repr(question)}\n\n"
            "Posibles respuestas:\n"
            f"{answer_lines}\n\n"
            "Compara todas las opciones en conjunto y devuelve el ID de la mejor respuesta."
        )
        
        images: list[str] = []
        for item in (question, *answers):
            img_b64 = item.get("image_b64")
            if img_b64 and img_b64 not in images:
                images.append(img_b64)
        out = self.llm.chat_structured(
            system_prompt=B_AUDIT_SYSTEM,
            user_prompt=user_prompt,
            response_model=PathBAuditBatchOutput,
            images=images,
        )
        self._trace(
            f"[path-b-audit-batch] selected={out.selected_answer_id or 'Ninguna'}"
        )
        return out