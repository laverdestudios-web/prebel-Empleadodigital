"""
Consola Interactiva para Probar el Asistente Prebel en Vivo.
Ejecuta: python test_cli.py
"""
import sys
from pathlib import Path

# Agregar directorio brain al path
sys.path.append(str(Path(__file__).parent / "brain"))

from agent import get_agent


def main():
    print("\n" + "=" * 65)
    print("🤖  BIENVENIDO AL TESTER DEL ASISTENTE DE GESTIÓN HUMANA")
    print("🏢  PREBEL S.A.S. BIC - EstudIA Reto 7")
    print("=" * 65)
    print("Escribe tu pregunta como si fueras un empleado de Prebel.")
    print("Escribe 'salir' para terminar.\n")
    
    agent = get_agent()
    history = []
    
    while True:
        try:
            user_input = input("\n👤 Tú: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["salir", "exit", "quit"]:
                print("\n👋 ¡Hasta luego!\n")
                break
                
            print("\n⏳ Consultando base de conocimientos...")
            result = agent.ask(user_input, history=history)
            
            print("\n" + "-" * 60)
            print("📋 RESPUESTA DEL ASISTENTE:")
            print("-" * 60)
            print(result["answer"])
            
            usage = result.get("usage")
            if usage:
                print("\n" + "." * 60)
                print(f"  Modelo: {usage['model']} | stop_reason: {usage['stop_reason']}")
                print(f"  Tokens entrada: {usage['input_tokens']} | caché leída: {usage['cache_read_input_tokens']}"
                      f" | caché escrita: {usage['cache_creation_input_tokens']} | salida: {usage['output_tokens']}")
                print("." * 60)

            if not result.get("error"):
                history += [
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": result["answer"]},
                ]
                
        except KeyboardInterrupt:
            print("\n👋 Sesión terminada.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
