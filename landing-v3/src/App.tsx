import { useEffect, useRef, useState } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { ASSETS } from "./config";
import Header from "./components/Header";
import Hero from "./components/Hero";
import Features from "./components/Features";
import PortraitCanvas, { type ZoomState } from "./components/PortraitCanvas";
import Hud from "./components/Hud";
import LensStack from "./components/LensStack";
import About from "./components/About";
import VoiceDock from "./components/VoiceDock";
import s from "./App.module.css";

gsap.registerPlugin(ScrollTrigger);

/** Escena de scroll: 3 unidades = 3 pantallas de desplazamiento (la escena mide 400svh). */
const SCENE = {
  zoom: [0, 1],
  hudIn: [0.65, 0.4],
  ringTurn: [0.65, 1.05],
  scanIn: [0.75, 0.3],
  meshIn: [0.95, 0.25],
  track: [1.0, 0.7],
  wash: [1.4, 0.35],
  hudOut: [1.4, 0.3],
  lensIn: [1.5, 0.4],
  spread: [2.2, 0.6],
  end: 3,
} as const;

const LENS_BLUR = 16;

type Ready = { image: ImageBitmap | null } | null;

export default function App() {
  const rootRef = useRef<HTMLElement>(null);
  const zoomRef = useRef<ZoomState>({ zoom: 0, extra: 0 });
  const [ready, setReady] = useState<Ready>(null);
  const [active, setActive] = useState<number | null>(null);

  // 1. Cargar el retrato (fetch → blob → ImageBitmap) y las dos fuentes antes de arrancar.
  useEffect(() => {
    let stale = false;
    let bitmap: ImageBitmap | null = null;
    const img = fetch(ASSETS.portrait)
      .then((r) => {
        if (!r.ok) throw new Error(`Retrato: HTTP ${r.status}`);
        return r.blob();
      })
      .then((b) => createImageBitmap(b))
      .catch((err) => {
        console.error(err);
        return null;
      });
    const fonts = Promise.all([
      document.fonts.load('400 1em "Instrument Sans"'),
      document.fonts.load('500 1em "Instrument Sans"'),
    ]).catch(() => undefined);
    Promise.all([img, fonts]).then(([b]) => {
      bitmap = b;
      if (stale) b?.close();
      else setReady({ image: b });
    });
    return () => {
      stale = true;
      bitmap?.close();
    };
  }, []);

  // 2. Entrada y escena de scroll.
  useEffect(() => {
    const root = rootRef.current;
    if (!ready || !root) return;
    const q = gsap.utils.selector(root);
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const lensEl = q('[data-scene="lens"]')[0] as HTMLElement;
    const zoom = zoomRef.current;

    const ctx = gsap.context(() => {
      // ---- M1 · Entrada
      const reveal = ["header", "label", "body", "buttons", "scroll", "callout"].map((k) => q(`[data-reveal="${k}"]`));
      if (reduced) {
        gsap.to([q('[data-scene="portrait"]'), ...reveal, q('[data-reveal="headline"]')], {
          opacity: 1,
          duration: 0.4,
          ease: "power1.out",
        });
      } else {
        const rise = (y: number, blur: number) => ({ from: { opacity: 0, y, filter: `blur(${blur}px)` }, to: { opacity: 1, y: 0, filter: "blur(0px)", clearProps: "filter,transform" } });
        const intro = gsap.timeline({ defaults: { ease: "power2.out" } });
        intro.fromTo(q('[data-scene="portrait"]'), { opacity: 0, filter: "blur(40px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.6, clearProps: "filter" }, 0);
        const r24 = rise(24, 8);
        intro.fromTo(q('[data-reveal="header"]'), r24.from, { ...r24.to, duration: 0.45 }, 0.1);
        const r20 = rise(20, 8);
        intro.fromTo(q('[data-reveal="label"]'), r20.from, { ...r20.to, duration: 0.45 }, 0.1);
        const r30 = rise(30, 8);
        intro.fromTo(q('[data-reveal="body"]'), r30.from, { ...r30.to, duration: 0.5 }, 0.35);
        intro.set(q('[data-reveal="headline"]'), { opacity: 1 }, 0.35);
        const chars = { from: { opacity: 0, yPercent: 35, filter: "blur(12px)" }, to: { opacity: 1, yPercent: 0, filter: "blur(0px)", duration: 0.4, stagger: 0.02, clearProps: "filter,transform" } };
        intro.fromTo(q('[data-line="1"] [data-char]'), chars.from, chars.to, 0.35);
        intro.fromTo(q('[data-line="2"] [data-char]'), chars.from, chars.to, 0.47);
        intro.fromTo(q('[data-reveal="buttons"]'), r20.from, { ...r20.to, duration: 0.5 }, 0.55);
        intro.fromTo(q('[data-reveal="scroll"]'), r20.from, { ...r20.to, duration: 0.5 }, 0.6);
        const r16 = rise(16, 10);
        intro.fromTo(q('[data-reveal="callout"]'), r16.from, { ...r16.to, duration: 0.4 }, 0.95);
      }

      // ---- M2 · Escena de scroll
      const tl = gsap.timeline({
        defaults: { ease: "none" },
        scrollTrigger: { trigger: q('[data-scene="scene"]')[0], start: "top top", end: "bottom bottom", scrub: 1 },
      });
      const at = (k: Exclude<keyof typeof SCENE, "end">): readonly [number, number] => SCENE[k];

      if (!reduced) {
        // El video MAGI-2 ya trae su propia aceleración: el scroll lo recorre en línea recta
        tl.fromTo(zoom, { zoom: 0 }, { zoom: 1, duration: at("zoom")[1], ease: "none" }, at("zoom")[0]);
        tl.fromTo(q('[data-scene="hud"]'), { opacity: 0, scale: 0.9 }, { opacity: 1, scale: 1, duration: at("hudIn")[1], ease: "power2.out" }, at("hudIn")[0]);
        tl.fromTo(q("[data-draw]"), { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: at("hudIn")[1], ease: "power2.out" }, at("hudIn")[0]);
        tl.fromTo(q('[data-scene="hud-ring"]'), { rotation: -20, svgOrigin: "0 0" }, { rotation: 25, svgOrigin: "0 0", duration: at("ringTurn")[1] }, at("ringTurn")[0]);
        tl.fromTo(q('[data-scene="hud-scan"]'), { opacity: 0 }, { opacity: 1, duration: at("scanIn")[1] }, at("scanIn")[0]);
        tl.fromTo(q('[data-scene="hud-label"]'), { opacity: 0, x: (i: number) => (i % 2 ? 14 : -14) }, { opacity: 1, x: 0, duration: 0.12, stagger: 0.07, ease: "power2.out" }, 0.82);
        tl.fromTo(q('[data-scene="hud-mesh"]'), { opacity: 0, scale: 0.92, svgOrigin: "0 0" }, { opacity: 1, scale: 1, svgOrigin: "0 0", duration: at("meshIn")[1], ease: "power2.out" }, at("meshIn")[0]);
      }
      tl.fromTo(q('[data-scene="veil"]'), { opacity: 1 }, { opacity: 0, duration: 0.6 }, 0);
      tl.fromTo(q('[data-scene="track"]'), { yPercent: 0 }, { yPercent: -50, duration: at("track")[1], ease: "power1.inOut" }, at("track")[0]);
      if (!reduced) {
        tl.fromTo(zoom, { extra: 0 }, { extra: 1, duration: at("wash")[1], ease: "power1.in" }, at("wash")[0]);
      }
      tl.fromTo(q('[data-scene="wash"]'), { opacity: 0 }, { opacity: 1, duration: at("wash")[1], ease: "power1.inOut" }, at("wash")[0]);
      if (!reduced) {
        tl.to(q('[data-scene="hud"]'), { opacity: 0, scale: 1.3, duration: at("hudOut")[1], ease: "power1.in" }, at("hudOut")[0]);
        tl.fromTo(lensEl, { opacity: 0, scale: 1.6 }, { opacity: 1, scale: 1, duration: at("lensIn")[1], ease: "power2.out" }, at("lensIn")[0]);
        const blur = { px: LENS_BLUR };
        tl.fromTo(
          blur,
          { px: LENS_BLUR },
          {
            px: 0,
            duration: at("lensIn")[1],
            ease: "power2.out",
            onUpdate: () => {
              lensEl.style.filter = blur.px > 0.05 && blur.px < LENS_BLUR - 0.05 ? `blur(${blur.px}px)` : "";
            },
          },
          at("lensIn")[0],
        );
        tl.fromTo(lensEl, { "--spread": 0 }, { "--spread": 1, duration: at("spread")[1], ease: "power2.inOut" }, at("spread")[0]);
      } else {
        gsap.set(lensEl, { "--spread": 1 });
        tl.fromTo(lensEl, { opacity: 0 }, { opacity: 1, duration: at("lensIn")[1] }, at("lensIn")[0]);
      }
      tl.set({}, {}, SCENE.end);

      // Secciones de información: entran al aparecer
      q("[data-fade]").forEach((el) => {
        gsap.fromTo(el, { opacity: 0, y: reduced ? 0 : 28 }, { opacity: 1, y: 0, duration: 0.7, ease: "power2.out", scrollTrigger: { trigger: el, start: "top 88%" } });
      });
    }, root);

    return () => {
      ctx.revert();
      lensEl.style.filter = "";
    };
  }, [ready]);

  return (
    <main ref={rootRef} className={s.main}>
      <Header />
      <div className={s.scene} data-scene="scene">
        <div className={s.pin}>
          <div className={s.stage}>
            <PortraitCanvas image={ready?.image ?? null} state={zoomRef} />
            <div className={s.veil} data-scene="veil" />
            <div className={s.wash} data-scene="wash" />
            <Hud />
            <LensStack active={active} />
          </div>
          <div className={s.track} data-scene="track">
            <Hero />
            <Features active={active} setActive={setActive} />
          </div>
        </div>
      </div>
      <About />
      <VoiceDock />
    </main>
  );
}
