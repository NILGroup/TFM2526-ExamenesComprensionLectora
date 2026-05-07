import json

def check_dataset_and_answers(dataset_file, answers_file):
    # Cargar el dataset de preguntas
    with open(dataset_file, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
        
    # Cargar el fichero de respuestas
    with open(answers_file, 'r', encoding='utf-8') as f:
        answers = json.load(f)
        
    # Extraer las preguntas y sus opciones válidas
    questions_dict = {}
    for exam in dataset.get('exams', []):
        for exercise_obj in exam.get('exercises', []):
            exercise = exercise_obj.get('exercise', {})
            for question in exercise.get('questions', []):
                q_id = question.get('questionId')
                # Obtenemos las letras de las opciones (A, B, C, etc.)
                options = [opt.get('optionId') for opt in question.get('options', [])]
                questions_dict[q_id] = options
                
    num_questions = len(questions_dict)
    num_answers = len(answers)
    
    print("=== Comprobación de Cantidades ===")
    print(f"Número de preguntas en el dataset: {num_questions}")
    print(f"Número de respuestas en el fichero: {num_answers}")
    
    if num_questions == num_answers:
        print("✓ El número de preguntas y respuestas ES EL MISMO.\n")
    else:
        print("✗ El número de preguntas y respuestas es DIFERENTE.\n")
        
    # Comprobar si las respuestas pertenecen a las opciones de su pregunta
    print("=== Comprobación de Opciones Válidas ===")
    invalid_answers = {}
    
    for q_id, valid_options in questions_dict.items():
        if q_id in answers:
            ans = answers[q_id]
            if ans not in valid_options:
                invalid_answers[q_id] = {'provided': ans, 'valid_options': valid_options}
                
    if len(invalid_answers) == 0:
        print("✓ Todas las respuestas coinciden con una de las opciones válidas de su pregunta.")
    else:
        print(f"✗ Se encontraron {len(invalid_answers)} respuestas que NO pertenecen a las opciones de su pregunta:")
        for q_id, info in invalid_answers.items():
            print(f"  - Pregunta {q_id}: respondió '{info['provided']}', pero las opciones eran {info['valid_options']}")

# Ejecutar la comprobación con tus ficheros
check_dataset_and_answers('../data/test_dataset/multiple_choice_dataset.json', '../data/zs_gemma4_test_formatted.json')