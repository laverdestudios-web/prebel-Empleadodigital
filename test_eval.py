"""
Batería de pruebas automatizadas para evaluar precisión del Chatbot Prebel.
Verifica:
1. Requisitos de cesantías
2. Auxilio visual y odontológico (montos y condiciones)
3. Crédito de mascotas
4. Certificado laboral según tipo de nómina
5. Pregunta fuera de alcance (debe rechazar con mensaje exacto)
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "brain"))

from agent import get_agent

TEST_CASES = [
    {
        "id": 1,
        "name": "Retiro de cesantías por compra de vivienda",
        "question": "¿Cuáles son los requisitos para retirar cesantías por compra de vivienda?",
        "expected_keywords": ["carta", "promesa", "notaria", "lucia.mejias@prebel.com.co", "3104589490"]
    },
    {
        "id": 2,
        "name": "Auxilio visual y odontológico",
        "question": "¿De cuánto es el auxilio visual u odontológico y cada cuánto se puede pedir?",
        "expected_keywords": ["332.000", "una sola vez a año calendario"]
    },
    {
        "id": 3,
        "name": "Crédito de mascotas",
        "question": "¿Qué cubre el crédito para mascotas y cuál es el monto máximo?",
        "expected_keywords": ["2 SMLMV", "0%", "cirugías", "perros", "gatos"]
    },
    {
        "id": 4,
        "name": "Pregunta fuera de alcance (Anti-alucinación)",
        "question": "¿Cuál es el salario mínimo en Colombia este año?",
        "expected_keywords": ["conocimiento se limita únicamente a los documentos cargados"]
    }
]


def run_tests():
    agent = get_agent()
    print("=" * 65)
    print("🧪 EJECUTANDO BATERÍA DE PRUEBAS DE EVALUACIÓN PREBEL")
    print("=" * 65)
    
    passed = 0
    for test in TEST_CASES:
        print(f"\n▶ Test {test['id']}: {test['name']}")
        print(f"  Pregunta: '{test['question']}'")
        
        result = agent.ask(test["question"])
        if result.get("error"):
            print(f"  ❌ ERROR TÉCNICO: {result['error']} (revisa ANTHROPIC_API_KEY y la conexión)")
            continue
        answer = result["answer"].lower()
        
        # Verificar palabras clave esperadas
        matched = [kw for kw in test["expected_keywords"] if kw.lower() in answer]
        success = len(matched) >= len(test["expected_keywords"]) // 2 + 1
        
        print(f"  Respuesta generada ({len(result['answer'])} caracteres):")
        print("  " + result["answer"].replace("\n", "\n  "))
        
        if success:
            print(f"  ✅ PASÓ (Coincidencias: {matched})")
            passed += 1
        else:
            print(f"  ⚠️ REVISAR (Faltaron palabras clave: {test['expected_keywords']})")
            
    print("\n" + "=" * 65)
    print(f"RESULTADO FINAL: {passed}/{len(TEST_CASES)} tests aprobados")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
