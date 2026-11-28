import { useEffect, useRef } from "react";
import s from "./Cursor.module.css";

/** Fracción de la distancia que recorre por cuadro a 60 fps. */
const FOLLOW = 0.3;

export default function Cursor() {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el || !window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;
    const pos = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
    const target = { ...pos };
    let lastT = performance.now();
    let raf = 0;

    const onMove = (e: MouseEvent) => {
      target.x = e.clientX;
      target.y = e.clientY;
      el.dataset.visible = "true";
    };
    const onOut = (e: MouseEvent) => {
      if (!e.relatedTarget) el.dataset.visible = "false";
    };
    const tick = (t: number) => {
      raf = requestAnimationFrame(tick);
      const k = 1 - Math.pow(1 - FOLLOW, (t - lastT) / 16.67);
      lastT = t;
      pos.x += (target.x - pos.x) * k;
      pos.y += (target.y - pos.y) * k;
      el.style.transform = `translate3d(${pos.x}px, ${pos.y}px, 0)`;
    };
    window.addEventListener("mousemove", onMove);
    document.addEventListener("mouseout", onOut);
    raf = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseout", onOut);
    };
  }, []);

  return (
    <div ref={ref} className={s.anchor} data-visible="false" aria-hidden="true">
      <div className={s.disc} />
    </div>
  );
}
