import { StrictMode, Suspense, lazy, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles/tokens.css";
import "./styles/global.css";
import App from "./App.tsx";
import Cursor from "./components/Cursor.tsx";

// La presentación vive en #presentacion (o #presentacion/3 para abrir en una diapositiva). Se carga solo cuando se abre.
const Presentation = lazy(() => import("./presentation/Presentation.tsx"));
const isPresentation = () => window.location.hash.startsWith("#presentacion");

function Root() {
  const [presenting, setPresenting] = useState(isPresentation);
  useEffect(() => {
    const onHash = () => {
      const next = isPresentation();
      setPresenting((prev) => {
        if (prev !== next) window.scrollTo(0, 0);
        return next;
      });
    };
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);
  return presenting ? (
    <Suspense fallback={null}>
      <Presentation />
    </Suspense>
  ) : (
    <App />
  );
}

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Root />
    <Cursor />
  </StrictMode>,
);
