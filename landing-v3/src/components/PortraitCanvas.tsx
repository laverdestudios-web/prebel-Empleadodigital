import { useEffect, useRef, type RefObject } from "react";
import s from "./PortraitCanvas.module.css";

/**
 * Retrato de SARHA y la entrada a su ojo.
 * - Arriba de la página: el primer cuadro del video, quieto (Juan descartó que siguiera el cursor).
 * - Al hacer scroll: el video MAGI-2 (public/sarha/zoom.mp4, 130 cuadros, todos keyframes).
 *   No se reproduce: el scroll elige el cuadro y se dibuja en el canvas.
 * - Si los cuadros aún no cargan, se usa el zoom de respaldo sobre la foto 4K.
 */

const base = import.meta.env.BASE_URL;

/** Iris en la foto 4K (respaldo). */
const IRIS = { x: 2160, y: 943, r: 51 };
/** Radio del iris en pantalla cuando el escáner lo encierra, en px de diseño (escritorio / celular). */
const IRIS_ON_SCREEN_DESKTOP = 210;
const IRIS_ON_SCREEN_MOBILE = 150;
const TOP_BIAS = 0.25;
const EXTRA_PUSH = 0.3;
const LEFT_BIAS = 0.85;
const FACE_X = 2010;
const ROLL_DEG = 1.6;

/** Video MAGI-2: 130 cuadros a 25 fps, medidos en 1920 × 1080 (el archivo web es de 1440 × 810). */
const ZOOM_FRAMES = 130;
const VIDEO_FPS = 25;
const VID = { w: 1920, h: 1080 };
/** Iris medido en cuadros clave del video (cuadro, centro x, centro y, radio) en px de 1920 × 1080. */
const IRIS_TRACK: [number, number, number, number][] = [
  [0, 1012, 442, 24],
  [70, 1005, 464, 108],
  [84, 1005, 472, 173],
  [96, 994, 500, 263],
  [106, 1000, 500, 354],
  [116, 977, 486, 472],
  [129, 970, 516, 590],
];

function irisAt(f: number) {
  for (let i = 1; i < IRIS_TRACK.length; i++) {
    const [f1, x1, y1, r1] = IRIS_TRACK[i];
    if (f <= f1) {
      const [f0, x0, y0, r0] = IRIS_TRACK[i - 1];
      const t = (f - f0) / (f1 - f0);
      return { x: x0 + (x1 - x0) * t, y: y0 + (y1 - y0) * t, r: r0 + (r1 - r0) * t };
    }
  }
  const [, x, y, r] = IRIS_TRACK[IRIS_TRACK.length - 1];
  return { x, y, r };
}

/** Primer cuadro en el que el iris alcanza ese radio (px del video). */
function frameForRadius(r: number) {
  for (let i = 1; i < IRIS_TRACK.length; i++) {
    const [f0, , , r0] = IRIS_TRACK[i - 1];
    const [f1, , , r1] = IRIS_TRACK[i];
    if (r <= r1) return f0 + ((r - r0) / (r1 - r0)) * (f1 - f0);
  }
  return ZOOM_FRAMES - 1;
}

export type ZoomState = { zoom: number; extra: number };

type Props = { image: ImageBitmap | null; state: RefObject<ZoomState> };

const smooth = (a: number, b: number, x: number) => {
  const t = Math.max(0, Math.min(1, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
};

export default function PortraitCanvas({ image, state }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const probeRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const probe = probeRef.current;
    if (!canvas || !probe || !image) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Video del zoom (MAGI-2) con todos los cuadros independientes (keyframes): saltar a cualquier
    // cuadro es instantáneo y la memoria queda baja. No se reproduce: el scroll elige el cuadro.
    const video = document.createElement("video");
    video.muted = true;
    video.playsInline = true;
    video.preload = "auto";
    video.src = `${base}sarha/zoom.mp4`;
    let videoOk = false;
    let seeking = false;
    let wantTime = -1;
    let shownTime = -1;
    const seek = (t: number) => {
      wantTime = t;
      if (seeking) return;
      seeking = true;
      video.currentTime = t;
    };
    const onLoaded = () => {
      videoOk = true;
      dirty = true;
    };
    const onSeeked = () => {
      seeking = false;
      shownTime = video.currentTime;
      dirty = true;
      if (Math.abs(wantTime - video.currentTime) > 0.01) seek(wantTime); // ya se pidió otro cuadro
    };
    video.addEventListener("loadeddata", onLoaded);
    video.addEventListener("seeked", onSeeked);
    video.load();

    const mobile = window.matchMedia("(max-width: 1023px)");
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let W = 0;
    let H = 0;
    let dpr = 1;
    // Solo se redibuja cuando cambia algo (scroll, tamaño o un cuadro nuevo cargado)
    let dirty = true;
    let lastKey = "";

    const ro = new ResizeObserver(() => {
      const r = canvas.getBoundingClientRect();
      dpr = Math.min(window.devicePixelRatio || 1, 1.5);
      W = r.width;
      H = r.height;
      canvas.width = Math.max(1, Math.round(W * dpr));
      canvas.height = Math.max(1, Math.round(H * dpr));
      dirty = true;
    });
    ro.observe(canvas);

    let visible = true;
    const io = new IntersectionObserver(([e]) => (visible = e.isIntersecting));
    io.observe(canvas);

    let raf = 0;
    const tick = () => {
      raf = requestAnimationFrame(tick);
      if (!W || !H || !visible) return;
      const { zoom, extra } = state.current;
      const key = `${zoom.toFixed(4)}|${extra.toFixed(4)}|${videoOk ? 1 : 0}|${shownTime}`;
      if (!dirty && key === lastKey) return;
      dirty = false;
      lastKey = key;
      const unit = probe.getBoundingClientRect().width / 100;
      const irisTarget = (mobile.matches ? IRIS_ON_SCREEN_MOBILE : IRIS_ON_SCREEN_DESKTOP) * unit;

      // Encuadre de la portada (foto 4K): cubre la pantalla, SARHA un poco a la derecha
      const s0 = Math.max(W / image.width, H / image.height);
      const minLeft = W - image.width * s0;
      const left0 = mobile.matches ? Math.min(0, Math.max(minLeft, W / 2 - FACE_X * s0)) : minLeft * LEFT_BIAS;
      const top0 = (H - image.height * s0) * TOP_BIAS;
      const roll = reduced ? 0 : ((ROLL_DEG * Math.PI) / 180) * Math.sin(Math.PI * Math.min(1, zoom));

      const begin = () => {
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.globalAlpha = 1;
        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = "high";
        ctx.fillStyle = "#e9f2f3";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      };
      const rolled = () => {
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.rotate(roll);
        ctx.translate(-canvas.width / 2, -canvas.height / 2);
        ctx.scale(dpr, dpr);
      };

      begin();

      const videoReady = videoOk && !reduced;
      if (videoReady) {
        // ---- Entrada al ojo con los cuadros de MAGI-2
        const sc = Math.max(W / VID.w, H / VID.h); // el video ocupa el mismo rectángulo que la foto
        const fLock = Math.max(10, Math.min(ZOOM_FRAMES - 2, frameForRadius(irisTarget / sc)));
        const f = zoom < 1 ? zoom * fLock : fLock + extra * (ZOOM_FRAMES - 1 - fLock);
        const t = Math.min(video.duration || 5.2, (Math.round(f) + 0.5) / VIDEO_FPS);
        if (Math.abs(t - shownTime) > 0.01 && Math.abs(t - wantTime) > 0.01) seek(t);
        const hasFrame = shownTime >= 0;
        const iris = irisAt(f);
        const w = smooth(0, 1, zoom);
        const sV = sc * (1 + 0.06 * w); // un poco de margen para que el centrado no deje bordes
        const x0 = left0;
        const y0 = top0;
        const xE = W / 2 - iris.x * sV;
        const yE = H / 2 - iris.y * sV;
        const x = x0 + (xE - x0) * w;
        const y = y0 + (yE - y0) * w;
        const sB = sc + (sV - sc) * w;
        rolled();
        if (hasFrame) ctx.drawImage(video, x, y, VID.w * sB, VID.h * sB);
        else ctx.drawImage(image, left0, top0, image.width * s0, image.height * s0);
      } else {
        // ---- Respaldo: zoom sobre la foto 4K
        const q0 = { x: left0 + IRIS.x * s0, y: top0 + IRIS.y * s0 };
        const s1 = irisTarget / IRIS.r;
        const sNow = s0 * Math.pow(s1 / s0, reduced ? 0 : zoom);
        const ww = s1 === s0 ? 0 : (sNow - s0) / (s1 - s0);
        const qx = q0.x + (W / 2 - q0.x) * ww;
        const qy = q0.y + (H / 2 - q0.y) * ww;
        const scale = sNow * (1 + EXTRA_PUSH * extra);
        const sx = IRIS.x - qx / scale;
        const sy = IRIS.y - qy / scale;
        rolled();
        ctx.transform(scale, 0, 0, scale, -sx * scale, -sy * scale);
        ctx.drawImage(image, 0, 0);
      }
      ctx.globalAlpha = 1;
    };
    raf = requestAnimationFrame(tick);

    return () => {
      cancelAnimationFrame(raf);
      video.removeEventListener("loadeddata", onLoaded);
      video.removeEventListener("seeked", onSeeked);
      video.removeAttribute("src");
      video.load();
      ro.disconnect();
      io.disconnect();
    };
  }, [image, state]);

  return (
    <>
      <canvas ref={canvasRef} className={s.canvas} data-scene="portrait" aria-hidden="true" />
      <div ref={probeRef} className={s.probe} aria-hidden="true" />
    </>
  );
}
