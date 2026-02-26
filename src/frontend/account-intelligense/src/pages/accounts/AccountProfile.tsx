import { useEffect, useMemo, useRef, useState } from "react";
import AppShell from "../../components/layout/AppShell";

type HistoryItem = {
  name: string;
  sector: string;
  when: string;
  initial: string;
  color: string;
};

export default function AccountProfile() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState<string>("");
  const [popupOpen, setPopupOpen] = useState(false);
  const [analysisType, setAnalysisType] = useState("Análisis Completo");
  const [started, setStarted] = useState(false);

  const popupRef = useRef<HTMLDivElement | null>(null);
  const plusBtnRef = useRef<HTMLButtonElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const hasText = query.trim().length > 0;

  // ✅ “Docked” = composer abajo (cuando ya escribiste o ya inició)
  const composerDocked = started || hasText;

  const history = useMemo<HistoryItem[]>(
    () => [
      { name: "Kavak", sector: "E-commerce", when: "Hoy", initial: "K", color: "bg-black" },
      { name: "Banorte", sector: "Finanzas", when: "2 días", initial: "B", color: "bg-red-600" },
      { name: "Lenovo", sector: "Tecnología", when: "2 meses", initial: "L", color: "bg-blue-600" },
      { name: "FEMSA", sector: "Retail / Logística", when: "3 meses", initial: "F", color: "bg-orange-600" },
    ],
    []
  );

  useEffect(() => {
    function onDown(e: MouseEvent) {
      if (!popupOpen) return;
      const p = popupRef.current;
      const b = plusBtnRef.current;
      const target = e.target as Node;

      if (p && p.contains(target)) return;
      if (b && b.contains(target)) return;
      setPopupOpen(false);
    }
    window.addEventListener("mousedown", onDown);
    return () => window.removeEventListener("mousedown", onDown);
  }, [popupOpen]);

  // ✅ Si cambia la posición del composer, mantenemos el foco
  useEffect(() => {
    // solo intentamos enfocar si ya hay interacción (cuando aparece docked)
    if (composerDocked) {
      // pequeño delay para que el layout se estabilice
      requestAnimationFrame(() => inputRef.current?.focus());
    }
  }, [composerDocked]);

  const handleSend = () => {
    const text = query.trim();
    if (!text) return;

    setSubmittedQuery(text);
    setStarted(true);
    setQuery("");
    setPopupOpen(false);
    // aquí llamas tu endpoint
  };

  return (
    <AppShell activeKey="profile360">
      <div className="flex h-[calc(100dvh-140px)] gap-6">
        {/* Historial */}
        <section className="w-[360px] shrink-0 rounded-2xl border border-border bg-app shadow-sm h-full flex flex-col min-h-0">
          <div className="border-b border-border px-5 py-4">
            <div className="text-lg font-semibold">Historial de análisis</div>
            <div className="mt-3 flex items-center gap-2 rounded-2xl border border-border bg-card px-3 py-2">
              <span className="text-text-muted">
                <SearchIcon />
              </span>
              <input
                placeholder="Buscar cuenta..."
                className="w-full bg-transparent text-sm text-text-primary placeholder:text-text-muted outline-none"
              />
            </div>
          </div>

          <div className="min-h-0 flex-1 overflow-auto px-2 py-2">
            {history.map((h) => (
              <button
                key={h.name}
                className="flex w-full items-center gap-4 rounded-2xl border border-border bg-card px-4 py-4 text-left shadow-sm hover:bg-hover"
              >
                <div className={`flex h-11 w-11 items-center justify-center rounded-full ${h.color} text-sm font-bold text-white`}>
                  {h.initial}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm font-semibold text-text-primary">{h.name}</div>
                  <div className="truncate text-xs text-text-secondary">{h.sector}</div>
                </div>
                <div className="text-xs text-text-muted">{h.when}</div>
              </button>
            ))}
          </div>
        </section>

        {/* Chat */}
        <section className="min-w-0 flex-1 rounded-2xl border border-border bg-app shadow-sm h-full flex flex-col min-h-0">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-border px-6 py-4 shrink-0">
            <div className="flex items-center gap-3">
              <div className="grid h-10 w-10 place-items-center rounded-full bg-brand text-white">
                <BoltSmall />
              </div>
              <div className="leading-tight">
                <div className="flex items-center gap-2">
                  <div className="text-sm font-semibold">HPE Insight AI</div>
                  <span className="h-2 w-2 rounded-full bg-success" />
                </div>
                <div className="text-xs text-text-secondary">Asistente estratégico de cuentas</div>
              </div>
            </div>

            <button className="grid h-10 w-10 place-items-center rounded-xl border border-border bg-card text-text-secondary hover:bg-hover">
              <DotsIcon />
            </button>
          </div>

          <div className="relative flex flex-1 min-h-0 flex-col">
            {/* Área scrolleable */}
            <div className="min-h-0 flex-1 overflow-auto px-8 py-8 pb-44">
              {!started ? (
                !hasText ? (
                  <div className="flex h-full flex-col items-center justify-center text-center">
                    <h2 className="text-3xl font-semibold tracking-tight">
                      ¿Con qué cuenta quieres comenzar?
                    </h2>
                    {/* Nota: Ya NO renderizamos un composer aquí */}
                  </div>
                ) : (
                  <div className="flex h-full items-center justify-center text-center">
                    <div className="max-w-xl text-text-secondary">
                      Presiona{" "}
                      <span className="font-semibold text-text-primary">Enter</span>{" "}
                      o haz clic en{" "}
                      <span className="font-semibold text-text-primary">Enviar</span>{" "}
                      para iniciar el análisis.
                    </div>
                  </div>
                )
              ) : (
                <div className="space-y-4">
                  <Bubble
                    text={`Listo. Analizaré: "${submittedQuery}"\nTipo: ${analysisType}\n\nAquí aparecerán insights, señales y recomendaciones.`}
                  />
                </div>
              )}
            </div>

            {/* ✅ UN SOLO COMPOSER: solo cambia de posición (no se desmonta) */}
            <div
              className={[
                "z-20 w-full",
                composerDocked
                  ? "sticky bottom-0 border-t border-border bg-app px-8 py-5"
                  : // centrado (sin desmontar)
                    "absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 px-8",
              ].join(" ")}
            >
              <div className={composerDocked ? "" : "w-[min(720px,100%)]"}>
                <Composer
                  mode={composerDocked ? "bottom" : "center"}
                  query={query}
                  setQuery={setQuery}
                  popupOpen={popupOpen}
                  setPopupOpen={setPopupOpen}
                  analysisType={analysisType}
                  setAnalysisType={setAnalysisType}
                  popupRef={popupRef}
                  plusBtnRef={plusBtnRef}
                  onSend={handleSend}
                  inputRef={inputRef}
                />
              </div>
            </div>
          </div>
        </section>
      </div>
    </AppShell>
  );
}

/* ---------- UI helpers con TOKENS ---------- */

function Bubble({ text }: { text: string }) {
  return (
    <div
      className="max-w-[760px] rounded-2xl bg-card px-4 py-3 text-sm text-text-primary border border-border"
      style={{ whiteSpace: "pre-wrap" }}
    >
      {text}
    </div>
  );
}

function Composer({
  mode,
  query,
  setQuery,
  popupOpen,
  setPopupOpen,
  analysisType,
  setAnalysisType,
  popupRef,
  plusBtnRef,
  onSend,
  inputRef,
}: {
  mode: "center" | "bottom";
  query: string;
  setQuery: React.Dispatch<React.SetStateAction<string>>;
  popupOpen: boolean;
  setPopupOpen: React.Dispatch<React.SetStateAction<boolean>>;
  analysisType: string;
  setAnalysisType: React.Dispatch<React.SetStateAction<string>>;
  popupRef: React.RefObject<HTMLDivElement | null>;
  plusBtnRef: React.RefObject<HTMLButtonElement | null>;
  onSend: () => void;
  inputRef: React.RefObject<HTMLInputElement | null>;
}) {
  const options = [
    "Análisis Completo",
    "Detectar Oportunidades",
    "Mapear Stack Actual",
    "Analizar Madurez Digital",
  ];
  const openUp = mode === "bottom";

  return (
    <div className="relative">
      <div
        className={[
          "flex items-center gap-3 rounded-2xl border border-border bg-card px-3 py-3",
          mode === "center" ? "shadow-sm" : "",
        ].join(" ")}
      >
        <div className="relative">
          <button
            ref={plusBtnRef}
            type="button"
            onClick={() => setPopupOpen((v) => !v)}
            className="grid h-10 w-10 place-items-center rounded-xl border border-border bg-app text-text-secondary hover:bg-hover"
            aria-label="Opciones"
          >
            <PlusIcon />
          </button>

          {popupOpen && (
            <div
            ref={popupRef}
            className={[
              "absolute left-0 z-50 w-[260px] rounded-2xl border border-border bg-app p-3 shadow-xl",
              "max-h-[320px] overflow-auto",
              openUp ? "bottom-12" : "top-12",
            ].join(" ")}
          >
              <div className="px-2 pb-2 text-xs font-semibold text-text-muted">
                Tipo de Análisis
              </div>
              <div className="space-y-2">
                {options.map((opt) => {
                  const selected = analysisType === opt;
                  return (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => {
                        setAnalysisType(opt);
                        setPopupOpen(false);
                        // mantenemos foco en input
                        requestAnimationFrame(() => inputRef.current?.focus());
                      }}
                      className={[
                        "w-full rounded-xl px-4 py-3 text-left text-sm font-medium",
                        "transition-colors border border-transparent",
                        selected
                          ? "bg-brand-accent text-text-primary border-border"
                          : "bg-card text-text-primary hover:bg-hover",
                        "focus:outline-none focus:ring-2 focus:ring-brand/20",
                      ].join(" ")}
                    >
                      {opt}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        <input
          ref={inputRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              onSend();
            }
          }}
          placeholder="Ingresa la URL o nombre de la empresa a analizar..."
          className="h-10 min-w-0 flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-muted outline-none"
        />

        <button
          type="button"
          onClick={onSend}
          className="grid h-10 w-10 place-items-center rounded-full bg-brand text-white hover:bg-brand-dark"
          aria-label="Enviar"
        >
          <ArrowUpIcon />
        </button>
      </div>

      <div className="mt-2 flex items-center justify-between px-1 text-xs text-text-secondary">
        <span>
          Selección actual:{" "}
          <span className="font-semibold text-text-primary">{analysisType}</span>
        </span>
        <span className="inline-flex items-center gap-1 text-text-secondary">
          <BoltSmall /> Insight AI
        </span>
      </div>
    </div>
  );
}

/* ---------- Icons inline (sin lucide) ---------- */
function SearchIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path
        d="M10.5 3a7.5 7.5 0 1 0 4.7 13.3l3.5 3.5 1.4-1.4-3.5-3.5A7.5 7.5 0 0 0 10.5 3Zm0 2a5.5 5.5 0 1 1 0 11 5.5 5.5 0 0 1 0-11Z"
        fill="currentColor"
      />
    </svg>
  );
}
function PlusIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}
function ArrowUpIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path
        d="M12 19V5m0 0 6 6M12 5 6 11"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
function DotsIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path d="M6 12h.01M12 12h.01M18 12h.01" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}
function BoltSmall() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path d="M13 2 3 14h7l-1 8 10-12h-7l1-8Z" fill="currentColor" />
    </svg>
  );
}