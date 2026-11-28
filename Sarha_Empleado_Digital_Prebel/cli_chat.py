"""Interactive terminal CLI to test the Prebel Gestión Humana chatbot locally."""

from __future__ import annotations

import argparse
import sys

from app.chatbot import HRChatbot
from app.config import settings
from app.knowledge import KnowledgeBase


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prueba interactiva por terminal del Chatbot de Gestión Humana Prebel."
    )
    parser.add_argument(
        "--channel",
        choices=["web", "whatsapp"],
        default="web",
        help="Formato de salida: web o whatsapp (por defecto: web).",
    )
    parser.add_argument(
        "-q",
        "--query",
        type=str,
        default=None,
        help="Ejecuta una sola consulta y termina (útil para pruebas rápidas).",
    )
    args = parser.parse_args()

    kb = KnowledgeBase(settings.docs_dir)
    bot = HRChatbot(kb, settings)

    if args.query:
        resp = bot.answer(args.query, channel=args.channel)
        print(resp.answer)
        if resp.sources:
            print("\n[Fuentes]:")
            for src in resp.sources:
                print(f" - {src['file']} -> {src['section']}")
        return

    print("=" * 72)
    print(f" Sarha · Chatbot Gestión Humana Prebel ({len(kb.chunks)} secciones indexadas)")
    print(f" Modo: {bot._active_mode()} | Canal: {args.channel}")
    print(" Navega escribiendo el NÚMERO de la opción (0=atrás, 00=inicio)")
    print(" o escribe cualquier pregunta. Escribe 'salir' para terminar.")
    print("=" * 72)

    channel = args.channel
    session_id = "cli"
    welcome = bot.answer("hola", channel=channel, session_id=session_id)
    print(f"\nSarha:\n{welcome.answer}\n")

    while True:
        try:
            user_input = input("Tú (número o pregunta) > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n¡Hasta luego!")
            sys.exit(0)

        if not user_input:
            continue
        if user_input.lower() in {"salir", "exit", "quit"}:
            print("¡Hasta luego!")
            break
        if user_input.lower() == "canal whatsapp":
            channel = "whatsapp"
            print("[Canal cambiado a: whatsapp]\n")
            continue
        if user_input.lower() == "canal web":
            channel = "web"
            print("[Canal cambiado a: web]\n")
            continue

        resp = bot.answer(user_input, channel=channel, session_id=session_id)
        print(f"\nSarha:\n{resp.answer}")
        if resp.sources:
            print("\n[Fuentes consultadas]:")
            for src in resp.sources:
                print(f" - {src['file']} -> {src['section']}")
        print()


if __name__ == "__main__":
    main()
