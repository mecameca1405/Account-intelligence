import {
    useEffect,
    useRef,
    useState,
    type Dispatch,
    type RefObject,
    type SetStateAction,
  } from "react";
  import AppShell from "../../components/layout/AppShell";
  
  /* ===================== TYPES ===================== */
  
  type HistoryItem = {
    id: string;
    companyName: string; // desde URL (o extra)
    domain: string; // hostname sin www
    whenISO: string; // fecha ISO
    initial: string;
    color: string;
    analysisType: string;
    source: "main" | "additional";
    url?: string;
    companyNameExtra?: string;
    industry?: string;
  };
  
  type SubmissionPayload = {
    source: "main" | "additional";
    analysisType: string;
    urlOrName?: string;
    companyName?: string;
    industry?: string;
  };
  
  type InputSource = "main" | "additional" | null;
  
  /* ===================== HELPERS ===================== */
  
  // ✅ URL validation helper (acepta "empresa.com" y normaliza a https://empresa.com)
  function validateUrl(raw: string): { ok: boolean; normalized?: string; error?: string } {
    const v = raw.trim();
    if (!v) return { ok: false, error: "Ingresa una URL válida." };
  
    const withScheme = /^https?:\/\//i.test(v) ? v : `https://${v}`;
  
    try {
      const u = new URL(withScheme);
  
      // Solo http/https
      if (u.protocol !== "http:" && u.protocol !== "https:") {
        return { ok: false, error: "Solo se permiten URLs http o https." };
      }
  
      // Host con punto para evitar textos random
      const host = u.hostname ?? "";
      if (!host.includes(".") || host.startsWith(".") || host.endsWith(".")) {
        return { ok: false, error: "La URL debe incluir un dominio válido (ej. empresa.com)." };
      }
  
      // No espacios
      if (/\s/.test(v)) return { ok: false, error: "La URL no puede contener espacios." };
  
      return { ok: true, normalized: u.toString() };
    } catch {
      return { ok: false, error: "Eso no parece una URL válida. Ej: https://empresa.com" };
    }
  }
  
  function extractCompanyFromUrl(normalizedUrl: string) {
    const u = new URL(normalizedUrl);
    const host = u.hostname.replace(/^www\./i, ""); // quita www
    const first = host.split(".")[0] || host;
  
    const pretty = first
      .replace(/[-_]+/g, " ")
      .replace(/\b\w/g, (m) => m.toUpperCase());
  
    return { companyName: pretty, domain: host };
  }
  
  function formatWhen(whenISO: string) {
    const d = new Date(whenISO);
    const now = new Date();
    const ms = now.getTime() - d.getTime();
    const days = Math.floor(ms / (1000 * 60 * 60 * 24));
  
    if (days <= 0) return "Hoy";
    if (days === 1) return "1 día";
    if (days < 30) return `${days} días`;
  
    const months = Math.floor(days / 30);
    if (months === 1) return "1 mes";
    return `${months} meses`;
  }
  
  function pickColorFromString(input: string) {
    const colors = [
      "bg-black",
      "bg-red-600",
      "bg-blue-600",
      "bg-orange-600",
      "bg-emerald-600",
      "bg-purple-600",
      "bg-sky-600",
      "bg-pink-600",
    ];
  
    let hash = 0;
    for (let i = 0; i < input.length; i++) hash = (hash * 31 + input.charCodeAt(i)) >>> 0;
    return colors[hash % colors.length];
  }
  
  /* ===================== MAIN ===================== */
  
  export default function AccountProfile() {
    const [query, setQuery] = useState("");
    const [submittedQuery, setSubmittedQuery] = useState<string>(""); // compat
    const [popupOpen, setPopupOpen] = useState(false);
    const [analysisType, setAnalysisType] = useState("Análisis Completo");
    const [started, setStarted] = useState(false);
  
    // ✅ Info adicional
    const [extraCompanyName, setExtraCompanyName] = useState("");
    const [extraIndustry, setExtraIndustry] = useState("");
  
    // ✅ Exclusividad (pero con switch)
    const [inputSource, setInputSource] = useState<InputSource>(null);
  
    const [submittedPayload, setSubmittedPayload] = useState<SubmissionPayload | null>(null);
  
    // ✅ Error del campo principal (URL)
    const [urlError, setUrlError] = useState<string | null>(null);
  
    const popupRef = useRef<HTMLDivElement | null>(null);
    const plusBtnRef = useRef<HTMLButtonElement | null>(null);
    const inputRef = useRef<HTMLInputElement | null>(null);
    const companyRef = useRef<HTMLInputElement | null>(null);
  
    const composerDocked = started;
  
    /* ---------- HISTORIAL PERSISTENTE ---------- */
    const HISTORY_KEY = "hpe_profile360_history_v1";
  
    const [history, setHistory] = useState<HistoryItem[]>(() => {
      try {
        const raw = localStorage.getItem(HISTORY_KEY);
        return raw ? (JSON.parse(raw) as HistoryItem[]) : [];
      } catch {
        return [];
      }
    });
  
    useEffect(() => {
      try {
        localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
      } catch {
        // ignore
      }
    }, [history]);
  
    const mainValue = query.trim();
    const additionalHasValue = extraCompanyName.trim().length > 0 || extraIndustry.trim().length > 0;
  
    const mainLocked = inputSource === "additional";
    const additionalLocked = inputSource === "main";
  
    // ✅ Validación en vivo: solo si hay texto
    const mainValidation = mainValue ? validateUrl(mainValue) : { ok: false };
  
    // ✅ Habilitar envío:
    const canSend =
      (inputSource === "main" && mainValue.length > 0 && mainValidation.ok) ||
      (inputSource === "additional" && additionalHasValue) ||
      (inputSource === null &&
        ((mainValue.length > 0 && mainValidation.ok) || (mainValue.length === 0 && additionalHasValue)));
  
    // ✅ Switchers
    const switchToMain = () => {
      setInputSource("main");
      setExtraCompanyName("");
      setExtraIndustry("");
      setQuery("");
      setUrlError(null);
      requestAnimationFrame(() => inputRef.current?.focus());
    };
  
    const switchToAdditional = () => {
      setInputSource("additional");
      setQuery("");
      setPopupOpen(true);
      requestAnimationFrame(() => companyRef.current?.focus());
    };
  
    const resetSource = () => {
      setInputSource(null);
      setUrlError(null);
      requestAnimationFrame(() => inputRef.current?.focus());
    };
  
    // ✅ Close popup only on click outside
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
  
    useEffect(() => {
      if (composerDocked) requestAnimationFrame(() => inputRef.current?.focus());
    }, [composerDocked]);
  
    const handleSend = () => {
      const source: "main" | "additional" | null =
        inputSource ?? (mainValue ? "main" : additionalHasValue ? "additional" : null);
  
      if (!source) return;
  
      let payload: SubmissionPayload;
  
      if (source === "main") {
        if (!mainValue) return;
  
        const v = validateUrl(mainValue);
        if (!v.ok) {
          setUrlError(v.error ?? "URL inválida.");
          return; // ⛔️ NO deja enviar al bubble
        }
  
        const normalized = v.normalized!;
        const { companyName, domain } = extractCompanyFromUrl(normalized);
  
        payload = { source, analysisType, urlOrName: normalized };
  
        // ✅ agrega al historial (persistente)
        const item: HistoryItem = {
          id: (globalThis.crypto?.randomUUID?.() ?? `${Date.now()}_${Math.random()}`) as string,
          companyName,
          domain,
          whenISO: new Date().toISOString(),
          initial: (companyName[0] || "?").toUpperCase(),
          color: pickColorFromString(domain),
          analysisType,
          source,
          url: normalized,
        };
  
        setHistory((prev) => [item, ...prev]);
  
        setSubmittedPayload(payload);
        setSubmittedQuery(normalized);
        setStarted(true);
  
        setQuery("");
        setUrlError(null);
        return;
      }
  
      // additional
      if (!additionalHasValue) return;
  
      payload = {
        source,
        analysisType,
        companyName: extraCompanyName.trim() || undefined,
        industry: extraIndustry.trim() || undefined,
      };
  
      const companyNameExtra = extraCompanyName.trim() || "Sin nombre";
  
      const item: HistoryItem = {
        id: (globalThis.crypto?.randomUUID?.() ?? `${Date.now()}_${Math.random()}`) as string,
        companyName: companyNameExtra,
        domain: "",
        whenISO: new Date().toISOString(),
        initial: (companyNameExtra[0] || "?").toUpperCase(),
        color: pickColorFromString(companyNameExtra),
        analysisType,
        source,
        companyNameExtra,
        industry: extraIndustry.trim() || undefined,
      };
  
      setHistory((prev) => [item, ...prev]);
  
      setSubmittedPayload(payload);
      setSubmittedQuery(mainValue);
      setStarted(true);
  
      setExtraCompanyName("");
      setExtraIndustry("");
      setUrlError(null);
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
              {history.length === 0 ? (
                <div className="px-4 py-6 text-sm text-text-secondary">
                  Aún no tienes análisis guardados. Ingresa una URL para comenzar.
                </div>
              ) : (
                history.map((h) => (
                  <button
                    key={h.id}
                    className="flex w-full items-center gap-4 rounded-2xl border border-border bg-card px-4 py-4 text-left shadow-sm hover:bg-hover"
                  >
                    <div
                      className={`flex h-11 w-11 items-center justify-center rounded-full ${h.color} text-sm font-bold text-white`}
                    >
                      {h.initial}
                    </div>
  
                    <div className="min-w-0 flex-1">
                      <div className="truncate text-sm font-semibold text-text-primary">{h.companyName}</div>
                      <div className="truncate text-xs text-text-secondary">
                        {h.analysisType}
                        {h.domain ? ` • ${h.domain}` : ""}
                      </div>
                    </div>
  
                    <div className="text-xs text-text-muted">{formatWhen(h.whenISO)}</div>
                  </button>
                ))
              )}
            </div>
          </section>
  
          {/* Chat */}
          <section className="min-w-0 flex-1 rounded-2xl border border-border bg-app shadow-sm h-full flex flex-col min-h-0 overflow-hidden">
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
              {/* Scroll area */}
              <div className="min-h-0 flex-1 overflow-auto px-8 py-8 pb-44">
                {!started ? (
                  <div className="flex h-full flex-col items-center justify-center text-center">
                    <h2 className="text-3xl font-semibold tracking-tight">¿Con qué cuenta quieres comenzar?</h2>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <Bubble
                      text={[
                        `Entrada elegida: ${submittedPayload?.source === "main" ? "URL / Campo principal" : "Información Adicional"}`,
                        `Tipo de análisis: ${submittedPayload?.analysisType ?? analysisType}`,
                        submittedPayload?.source === "main"
                          ? `URL/Nombre: ${submittedPayload?.urlOrName ?? ""}`
                          : `Empresa: ${submittedPayload?.companyName ?? "(no especificada)"}\nIndustria: ${
                              submittedPayload?.industry ?? "(no especificada)"
                            }`,
                        ``,
                        `Aquí aparecerán insights, señales y recomendaciones.`,
                      ]
                        .filter(Boolean)
                        .join("\n")}
                    />
                  </div>
                )}
              </div>
  
              {/* ✅ Composer wrapper */}
              <div
                className={[
                  "z-20 w-full",
                  composerDocked
                    ? "sticky bottom-0 border-t border-border bg-app px-8 py-5"
                    : "absolute inset-x-0 top-1/2 -translate-y-1/2",
                ].join(" ")}
              >
                <div className={composerDocked ? "w-full" : "mx-auto w-full max-w-[1100px] px-4 sm:px-8"}>
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
                    companyRef={companyRef}
                    extraCompanyName={extraCompanyName}
                    setExtraCompanyName={setExtraCompanyName}
                    extraIndustry={extraIndustry}
                    setExtraIndustry={setExtraIndustry}
                    inputSource={inputSource}
                    setInputSource={setInputSource}
                    mainLocked={mainLocked}
                    additionalLocked={additionalLocked}
                    canSend={canSend}
                    switchToMain={switchToMain}
                    switchToAdditional={switchToAdditional}
                    resetSource={resetSource}
                    urlError={urlError}
                    setUrlError={setUrlError}
                  />
                </div>
              </div>
            </div>
          </section>
        </div>
      </AppShell>
    );
  }
  
  /* ---------- UI helpers ---------- */
  
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
    companyRef,
    extraCompanyName,
    setExtraCompanyName,
    extraIndustry,
    setExtraIndustry,
    inputSource,
    setInputSource,
    mainLocked,
    additionalLocked,
    canSend,
    switchToMain,
    switchToAdditional,
    resetSource,
    urlError,
    setUrlError,
  }: {
    mode: "center" | "bottom";
    query: string;
    setQuery: Dispatch<SetStateAction<string>>;
    popupOpen: boolean;
    setPopupOpen: Dispatch<SetStateAction<boolean>>;
    analysisType: string;
    setAnalysisType: Dispatch<SetStateAction<string>>;
    popupRef: RefObject<HTMLDivElement | null>;
    plusBtnRef: RefObject<HTMLButtonElement | null>;
    onSend: () => void;
    inputRef: RefObject<HTMLInputElement | null>;
    companyRef: RefObject<HTMLInputElement | null>;
    extraCompanyName: string;
    setExtraCompanyName: Dispatch<SetStateAction<string>>;
    extraIndustry: string;
    setExtraIndustry: Dispatch<SetStateAction<string>>;
    inputSource: InputSource;
    setInputSource: Dispatch<SetStateAction<InputSource>>;
    mainLocked: boolean;
    additionalLocked: boolean;
    canSend: boolean;
    switchToMain: () => void;
    switchToAdditional: () => void;
    resetSource: () => void;
    urlError: string | null;
    setUrlError: Dispatch<SetStateAction<string | null>>;
  }) {
    const options = ["Análisis Completo", "Detectar Oportunidades", "Mapear Stack Actual", "Analizar Madurez Digital"];
  
    const industries = [
      "Tecnología",
      "Finanzas",
      "Retail",
      "Manufactura",
      "Logística",
      "Salud",
      "Educación",
      "Gobierno",
      "E-commerce",
    ];
  
    const openUp = mode === "bottom";
    const isQueryEmpty = query.trim().length === 0;
  
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
  
            {/* ✅ POPUPS responsive */}
            {popupOpen && (
              <div
                ref={popupRef}
                className={[
                  "absolute left-0 z-50",
                  "w-[min(760px,calc(100vw-32px))] sm:w-[min(760px,calc(100vw-64px))]",
                  "grid grid-cols-1 sm:grid-cols-[260px_minmax(0,1fr)] gap-3 sm:gap-4",
                  openUp ? "bottom-12" : "top-12",
                ].join(" ")}
              >
                {/* Popup 1: Tipo de análisis */}
                <div
                  className={[
                    "w-full",
                    "rounded-2xl border border-border bg-app p-3 shadow-xl",
                    "max-h-[320px] overflow-auto",
                  ].join(" ")}
                >
                  <div className="px-2 pb-2 text-xs font-semibold text-text-muted">Tipo de Análisis</div>
  
                  <div className="space-y-2">
                    {options.map((opt) => {
                      const selected = analysisType === opt;
                      return (
                        <button
                          key={opt}
                          type="button"
                          onClick={() => {
                            setAnalysisType(opt);
                            requestAnimationFrame(() => inputRef.current?.focus());
                          }}
                          className={[
                            "w-full rounded-xl px-4 py-3 text-left text-sm font-medium",
                            "transition-colors border",
                            selected
                              ? "bg-brand-accent text-text-primary border-brand"
                              : "bg-card text-text-primary border-border hover:bg-hover",
                            "focus:outline-none focus:ring-2 focus:ring-border",
                            "flex items-center justify-between gap-3",
                          ].join(" ")}
                        >
                          <span>{opt}</span>
                          {selected ? (
                            <span className="grid h-6 w-6 place-items-center rounded-full bg-brand text-white">
                              <CheckIcon />
                            </span>
                          ) : (
                            <span className="h-6 w-6" />
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>
  
                {/* Popup 2: Información adicional (solo si query vacío) */}
                {isQueryEmpty && (
                  <div className={["w-full", "rounded-2xl border border-border bg-app p-4 shadow-xl"].join(" ")}>
                    <div className="mb-3 flex items-center justify-between gap-3">
                      <div className="text-sm font-semibold text-text-primary">Información Adicional:</div>
  
                      {additionalLocked && (
                        <button
                          type="button"
                          onClick={switchToAdditional}
                          className="rounded-xl border border-border bg-card px-3 py-2 text-xs font-semibold text-text-primary hover:bg-hover"
                        >
                          Cambiar aquí
                        </button>
                      )}
                    </div>
  
                    {additionalLocked && (
                      <div className="mb-3 rounded-xl border border-border bg-card p-3 text-xs text-text-secondary">
                        Estás usando el <span className="font-semibold text-text-primary">campo principal</span>. Haz clic en{" "}
                        <span className="font-semibold text-text-primary">“Cambiar aquí”</span>.
                      </div>
                    )}
  
                    <div className="space-y-3">
                      <div>
                        <label className="mb-1 block text-xs font-semibold text-text-muted">Empresa (opcional)</label>
  
                        <input
                          ref={companyRef}
                          value={extraCompanyName}
                          disabled={additionalLocked}
                          onChange={(e) => {
                            if (additionalLocked) return;
                            setInputSource("additional");
                            setExtraCompanyName(e.target.value);
                            setQuery("");
                          }}
                          placeholder={
                            additionalLocked
                              ? "Bloqueado: estás usando el campo principal"
                              : "Ingresa el nombre de la empresa a analizar..."
                          }
                          className={[
                            "h-11 w-full rounded-2xl border border-border bg-card px-4 text-sm outline-none",
                            "text-text-primary placeholder:text-text-muted",
                            additionalLocked ? "opacity-60 cursor-not-allowed" : "focus:border-brand",
                          ].join(" ")}
                        />
                      </div>
  
                      <div>
                        <label className="mb-1 block text-xs font-semibold text-text-muted">Industria (opcional)</label>
  
                        <div className="relative">
                          <select
                            value={extraIndustry}
                            disabled={additionalLocked}
                            onChange={(e) => {
                              if (additionalLocked) return;
                              setInputSource("additional");
                              setExtraIndustry(e.target.value);
                              setQuery("");
                            }}
                            className={[
                              "h-11 w-full appearance-none rounded-2xl border border-border bg-card px-4 pr-10 text-sm outline-none",
                              "text-text-primary",
                              additionalLocked ? "opacity-60 cursor-not-allowed" : "focus:border-brand",
                            ].join(" ")}
                          >
                            <option value="">Selecciona la Industria</option>
                            {industries.map((i) => (
                              <option key={i} value={i}>
                                {i}
                              </option>
                            ))}
                          </select>
  
                          <span className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-text-muted">
                            <ChevronDownIcon />
                          </span>
                        </div>
                      </div>
  
                      <div className="text-xs text-text-muted">
                        * Este panel solo aparece si aún no has escrito una URL en el campo principal.
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
  
          {/* ✅ CTA cuando main está bloqueado */}
          {mainLocked && (
            <button
              type="button"
              onClick={switchToMain}
              className="rounded-xl border border-border bg-card px-3 py-2 text-xs font-semibold text-text-primary hover:bg-hover"
            >
              Cambiar a campo principal
            </button>
          )}
  
          {/* ✅ INPUT PRINCIPAL (URL) */}
          <input
            ref={inputRef}
            value={query}
            disabled={mainLocked}
            onChange={(e) => {
              if (mainLocked) return;
  
              const next = e.target.value;
              setInputSource("main");
              setQuery(next);
              setExtraCompanyName("");
              setExtraIndustry("");
  
              // ✅ Valida en vivo y muestra error
              const trimmed = next.trim();
              if (!trimmed) {
                setUrlError(null);
              } else {
                const v = validateUrl(trimmed);
                setUrlError(v.ok ? null : v.error ?? "URL inválida.");
              }
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                if (!canSend) return;
                onSend();
              }
            }}
            placeholder={
              mainLocked ? "Bloqueado: estás usando Información Adicional" : "Ingresa la URL o nombre de la empresa a analizar..."
            }
            className={[
              "h-10 min-w-0 flex-1 bg-transparent text-sm outline-none",
              "text-text-primary placeholder:text-text-muted",
              mainLocked ? "opacity-60 cursor-not-allowed" : "",
            ].join(" ")}
          />
  
          <button
            type="button"
            onClick={onSend}
            disabled={!canSend}
            className={[
              "grid h-10 w-10 place-items-center rounded-full text-white",
              canSend ? "bg-brand hover:bg-brand-dark" : "bg-border cursor-not-allowed",
            ].join(" ")}
            aria-label="Enviar"
          >
            <ArrowUpIcon />
          </button>
        </div>
  
        {/* ✅ ERROR DE URL */}
        {!mainLocked && query.trim().length > 0 && urlError && (
          <div className="mt-2 rounded-xl border border-border bg-card px-3 py-2 text-xs text-text-secondary">
            <span className="font-semibold text-text-primary">URL inválida:</span> {urlError}
          </div>
        )}
  
        <div className="mt-2 flex items-center justify-between px-1 text-xs text-text-secondary">
          <span>
            Selección actual: <span className="font-semibold text-text-primary">{analysisType}</span>
          </span>
  
          <span className="inline-flex items-center gap-2 text-text-secondary">
            {inputSource ? (
              <span className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-2 py-1 text-[11px]">
                <span>Usando: {inputSource === "main" ? "Campo principal" : "Info adicional"}</span>
                <button
                  type="button"
                  onClick={resetSource}
                  className="rounded-full border border-border bg-app px-2 py-0.5 font-semibold hover:bg-hover"
                  title="Desbloquear ambos"
                >
                  Reset
                </button>
              </span>
            ) : (
              <span className="rounded-full border border-border bg-card px-2 py-1 text-[11px]">Usando: Auto</span>
            )}
  
            <span className="inline-flex items-center gap-1">
              <BoltSmall /> Insight AI
            </span>
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
  function ChevronDownIcon() {
    return (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
        <path
          d="M6 9l6 6 6-6"
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
  function CheckIcon() {
    return (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <path
          d="M20 6 9 17l-5-5"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    );
  }