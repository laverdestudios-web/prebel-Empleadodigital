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
    
    while True:
        try:
            user_input = input("\n👤 Tú: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["salir", "exit", "quit"]:
                print("\n👋 ¡Hasta luego!\n")
                break
                
            print("\n⏳ Consultando base de conocimientos...")
            result = agent.ask(user_input)
            
            print("\n" + "-" * 60)
            print("📋 RESPUESTA DEL ASISTENTE:")
            print("-" * 60)
            print(result["answer"])
            
            if result.get("sources"):
                print("\n" + "." * 60)
                print("🔍 FUENTES RECUPERADAS:")
                for s in result["sources"]:
                    print(f"  • [{s['score']}] {s['section']} ({s['source']})")
                print("." * 60)
                
        except KeyboardInterrupt:
            print("\n👋 Sesión terminada.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
