import {
  useEffect,
  useRef,
  useState,
  type Dispatch,
  type RefObject,
  type SetStateAction,
} from "react";
import AppShell from "../../components/layout/AppShell";
import {
  Search,
  Plus,
  ArrowUp,
  ChevronDown,
  MoreHorizontal,
  Zap,
  Check,
  PanelLeft,
  PanelRight,
} from "lucide-react";

/* ===================== API CONFIG ===================== */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const API_V1 = "/api/v1";

/* ===================== TYPES ===================== */

type Message = {
  id: string;
  role: "user" | "assistant";
  text: string;
  tsISO: string;
};

type ChatItem = {
  id: string;
  companyName: string;
  domain: string;
  whenISO: string; // última actividad
  initial: string;
  color: string;
  analysisType: string;
  url?: string;
  industryLabel?: string;
  industryId?: number;
  messages: Message[];
};

/* ===================== BACKEND TYPES ===================== */

type CreateAnalysisPayload = {
  company_name: string;
  website_url: string;
  industry_id: string;
};

type CreateAnalysisResponse = {
  analysis_id: number;
  status: string;
};

type ProgressResponse = {
  analysis_id: number;
  status: string;
  progress_percentage: number;
};

type Insight = {
  id: number;
  title: string;
  severity: string;
  description: string;
};

type Recommendation = {
  id: number;
  product_id: number;
  match_percentage: number;
  confidence_score: number;
  is_accepted: boolean | null;
};

type SalesStrategy = {
  id: number;
  status: string;
  account_strategic_overview?: string | null;
  priority_initiatives?: string | null;
  financial_positioning?: string | null;
  technical_enablement_summary?: string | null;
  objection_handling?: string | null;
  executive_conversation_version?: string | null;
  email_version?: string | null;
};

type FullAnalysisResponse = {
  analysis_id: number;
  company_id: number;
  company_name: string | null;
  status: string;
  strategic_score: number | null;
  propensity_score: number | null;
  insights: Insight[];
  recommendations: Recommendation[];
  sales_strategy: SalesStrategy | null;
};

/* ===================== HELPERS ===================== */

function uid() {
  return (globalThis.crypto?.randomUUID?.() ?? `${Date.now()}_${Math.random()}`) as string;
}

function validateUrl(raw: string): { ok: boolean; normalized?: string; error?: string } {
  const v = raw.trim();
  if (!v) return { ok: false, error: "Ingresa una URL válida." };

  const withScheme = /^https?:\/\//i.test(v) ? v : `https://${v}`;

  try {
    const u = new URL(withScheme);

    if (u.protocol !== "http:" && u.protocol !== "https:") {
      return { ok: false, error: "Solo se permiten URLs http o https." };
    }

    const host = u.hostname ?? "";
    if (!host.includes(".") || host.startsWith(".") || host.endsWith(".")) {
      return { ok: false, error: "La URL debe incluir un dominio válido (ej. empresa.com)." };
    }

    if (/\s/.test(v)) return { ok: false, error: "La URL no puede contener espacios." };

    return { ok: true, normalized: u.toString() };
  } catch {
    return { ok: false, error: "Eso no parece una URL válida. Ej: https://empresa.com" };
  }
}

function extractDomain(normalizedUrl: string) {
  const u = new URL(normalizedUrl);
  return u.hostname.replace(/^www\./i, "");
}

function truncateIfUrl(text: string, max = 90) {
  const t = text.trim();
  const looksLikeUrl = /^https?:\/\//i.test(t) || /^[\w-]+\.[a-z]{2,}/i.test(t);
  if (!looksLikeUrl) return text;
  if (t.length <= max) return t;
  return t.slice(0, max) + "…";
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

/* ===== Industry mapping (TEMP) =====
   Ajusta los IDs a los reales de tu BD si no coinciden.
*/
const INDUSTRIES = [
  "Tecnología",
  "Finanzas",
  "Retail",
  "Manufactura",
  "Logística",
  "Salud",
  "Educación",
  "Gobierno",
  "E-commerce",
] as const;

const INDUSTRY_ID_MAP: Record<(typeof INDUSTRIES)[number], number> = {
  "Tecnología": 1,
  "Finanzas": 2,
  "Retail": 3,
  "Manufactura": 4,
  "Logística": 5,
  "Salud": 6,
  "Educación": 7,
  "Gobierno": 8,
  "E-commerce": 9,
};

function getIndustryId(label: string): number {
  return (INDUSTRY_ID_MAP as any)[label] ?? 1;
}

function authHeaders() {
  const accessToken = localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
  };
}

async function apiJson<T>(path: string, init?: RequestInit) {
  const headers = new Headers(init?.headers || {});
  headers.set("Content-Type", "application/json");
  const accessToken = localStorage.getItem("access_token");
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
  });

  let data: any = null;
  try {
    data = await res.json();
  } catch {
    // ignore
  }

  if (!res.ok) {
    const detail =
      data?.detail ??
      data?.message ??
      `${res.status} ${res.statusText}` ??
      "Error desconocido";
    const err = new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    (err as any).status = res.status;
    (err as any).data = data;
    throw err;
  }

  return data as T;
}

function sleep(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

function formatFullAnalysisToChatText(full: FullAnalysisResponse) {
  const lines: string[] = [];

  lines.push(`✅ **Análisis completado**`);
  lines.push(`Cuenta: ${full.company_name ?? "(sin nombre)"}`);
  lines.push(`Status: ${full.status}`);
  lines.push(`Strategic score: ${full.strategic_score ?? "N/A"}  |  Propensity: ${full.propensity_score ?? "N/A"}`);
  lines.push("");

  if (full.insights?.length) {
    lines.push(`🧠 **Insights (${full.insights.length})**`);
    for (const i of full.insights.slice(0, 8)) {
      lines.push(`• [${i.severity}] ${i.title}`);
      if (i.description) lines.push(`  - ${i.description}`);
    }
    if (full.insights.length > 8) lines.push(`… +${full.insights.length - 8} más`);
    lines.push("");
  }

  if (full.recommendations?.length) {
    lines.push(`🎯 **Recomendaciones (${full.recommendations.length})**`);
    for (const r of full.recommendations.slice(0, 8)) {
      lines.push(
        `• Producto #${r.product_id} | match: ${r.match_percentage}% | confidence: ${r.confidence_score} | accepted: ${
          r.is_accepted ?? "N/A"
        }`
      );
    }
    if (full.recommendations.length > 8) lines.push(`… +${full.recommendations.length - 8} más`);
    lines.push("");
  }

  if (full.sales_strategy) {
    lines.push(`🗣️ **Sales Strategy (${full.sales_strategy.status})**`);
    if (full.sales_strategy.account_strategic_overview) {
      lines.push(`**Account strategic overview:**`);
      lines.push(full.sales_strategy.account_strategic_overview);
      lines.push("");
    }
    if (full.sales_strategy.executive_conversation_version) {
      lines.push(`**Executive conversation version:**`);
      lines.push(full.sales_strategy.executive_conversation_version);
      lines.push("");
    }
  }

  return lines.join("\n");
}

/* ===================== MAIN ===================== */

export default function AccountProfile() {
  // ✅ 3 CAMPOS OBLIGATORIOS
  const [urlInput, setUrlInput] = useState("");
  const [companyNameInput, setCompanyNameInput] = useState("");
  const [industryLabel, setIndustryLabel] = useState<string>("");

  const [urlError, setUrlError] = useState<string | null>(null);
  const [companyError, setCompanyError] = useState<string | null>(null);
  const [industryError, setIndustryError] = useState<string | null>(null);

  const [popupOpen, setPopupOpen] = useState(false);
  const [analysisType, setAnalysisType] = useState("Análisis Completo");

  // ✅ Minimizar sidebar
  const SIDEBAR_KEY = "hpe_profile360_sidebar_collapsed_v2";
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem(SIDEBAR_KEY) === "1";
    } catch {
      return false;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(SIDEBAR_KEY, sidebarCollapsed ? "1" : "0");
    } catch {
      // ignore
    }
  }, [sidebarCollapsed]);

  // ✅ Chats (historial + mensajes) y chat activo
  const CHATS_KEY = "hpe_profile360_chats_v1";
  const ACTIVE_KEY = "hpe_profile360_active_chat_v1";

  const [chats, setChats] = useState<ChatItem[]>(() => {
    try {
      const raw = localStorage.getItem(CHATS_KEY);
      return raw ? (JSON.parse(raw) as ChatItem[]) : [];
    } catch {
      return [];
    }
  });

  const [activeChatId, setActiveChatId] = useState<string | null>(() => {
    try {
      return localStorage.getItem(ACTIVE_KEY);
    } catch {
      return null;
    }
  });

  const activeChat = chats.find((c) => c.id === activeChatId) ?? null;

  useEffect(() => {
    try {
      localStorage.setItem(CHATS_KEY, JSON.stringify(chats));
    } catch {}
  }, [chats]);

  useEffect(() => {
    try {
      if (activeChatId) localStorage.setItem(ACTIVE_KEY, activeChatId);
      else localStorage.removeItem(ACTIVE_KEY);
    } catch {}
  }, [activeChatId]);

  const popupRef = useRef<HTMLDivElement | null>(null);
  const plusBtnRef = useRef<HTMLButtonElement | null>(null);
  const urlRef = useRef<HTMLInputElement | null>(null);
  const companyRef = useRef<HTMLInputElement | null>(null);

  // close popup outside
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

  function pushMessage(chatId: string, msg: Message) {
    setChats((prev) =>
      prev.map((c) =>
        c.id === chatId
          ? {
              ...c,
              whenISO: new Date().toISOString(),
              messages: [...c.messages, msg],
            }
          : c
      )
    );
  }

  function updateMessage(chatId: string, messageId: string, newText: string) {
    setChats((prev) =>
      prev.map((c) =>
        c.id === chatId
          ? {
              ...c,
              whenISO: new Date().toISOString(),
              messages: c.messages.map((m) => (m.id === messageId ? { ...m, text: newText } : m)),
            }
          : c
      )
    );
  }

  async function runAnalysisPipelineAndRender(chatId: string, payload: CreateAnalysisPayload, assistantMessageId: string) {
    // 1) Create analysis
    const created = await apiJson<CreateAnalysisResponse>(`${API_V1}/analysis/`, {
      method: "POST",
      headers: authHeaders(),
      body: JSON.stringify(payload),
    });

    updateMessage(
      chatId,
      assistantMessageId,
      [
        `⏳ Análisis creado (#${created.analysis_id}).`,
        `Estado: ${created.status}`,
        ``,
        `Procesando señales e insights…`,
      ].join("\n")
    );

    // 2) Poll progress
    let lastProgress = -1;
    for (let attempt = 0; attempt < 90; attempt++) {
      await sleep(1500);

      const prog = await apiJson<ProgressResponse>(`${API_V1}/analysis/${created.analysis_id}/progress`, {
        method: "GET",
        headers: authHeaders(),
      });

      if (prog.progress_percentage !== lastProgress) {
        lastProgress = prog.progress_percentage;
        updateMessage(
          chatId,
          assistantMessageId,
          [
            `⏳ Analizando… ${prog.progress_percentage}%`,
            `Estado: ${prog.status}`,
            ``,
            `En cuanto termine, te muestro el resultado aquí mismo.`,
          ].join("\n")
        );
      }

      if (prog.progress_percentage >= 100 || prog.status === "completed") break;
    }

    // 3) Get full
    const full = await apiJson<FullAnalysisResponse>(`${API_V1}/analysis/${created.analysis_id}/full`, {
      method: "GET",
      headers: authHeaders(),
    });

    updateMessage(chatId, assistantMessageId, formatFullAnalysisToChatText(full));
  }

  const handleNewChat = () => {
    const chatId = uid();
    const nowISO = new Date().toISOString();

    const newChat: ChatItem = {
      id: chatId,
      companyName: "Nuevo chat",
      domain: "",
      whenISO: nowISO,
      initial: "N",
      color: "bg-black",
      analysisType,
      messages: [],
    };

    setChats((prev) => [newChat, ...prev]);
    setActiveChatId(chatId);

    requestAnimationFrame(() => urlRef.current?.focus());
  };

  const validateAll = () => {
    const urlV = validateUrl(urlInput.trim());
    const cn = companyNameInput.trim();
    const ind = industryLabel.trim();

    setUrlError(urlV.ok ? null : urlV.error ?? "URL inválida.");
    setCompanyError(cn ? null : "El nombre de la empresa es obligatorio.");
    setIndustryError(ind ? null : "Selecciona una industria.");

    return { ok: urlV.ok && !!cn && !!ind, normalizedUrl: urlV.normalized };
  };

  const canSend = (() => {
    const urlV = urlInput.trim() ? validateUrl(urlInput.trim()) : { ok: false };
    return urlV.ok && companyNameInput.trim().length > 0 && industryLabel.trim().length > 0;
  })();

  const handleSend = () => {
    const { ok, normalizedUrl } = validateAll();
    if (!ok || !normalizedUrl) return;

    const normalized = normalizedUrl;
    const companyName = companyNameInput.trim();
    const domain = extractDomain(normalized);
    const indId = getIndustryId(industryLabel);

    const nowISO = new Date().toISOString();
    const userMsg: Message = {
      id: uid(),
      role: "user",
      text: `URL: ${normalized}\nEmpresa: ${companyName}\nIndustria: ${industryLabel}`,
      tsISO: nowISO,
    };

    const assistantMsgId = uid();
    const assistantMsg: Message = {
      id: assistantMsgId,
      role: "assistant",
      text: [
        `✅ Datos recibidos.`,
        `Tipo de análisis: ${analysisType}`,
        `URL: ${normalized}`,
        `Empresa: ${companyName}`,
        `Industria: ${industryLabel} (id: ${indId})`,
        ``,
        `⏳ Conectando con el backend para generar el análisis…`,
      ].join("\n"),
      tsISO: nowISO,
    };

    const payload: CreateAnalysisPayload = {
      company_name: companyName,
      website_url: normalized,
      industry: industryLabel, // ✅ string
    };

    // if no active chat → create one
    if (!activeChatId) {
      const chatId = uid();
      const newChat: ChatItem = {
        id: chatId,
        companyName,
        domain,
        whenISO: nowISO,
        initial: (companyName[0] || "?").toUpperCase(),
        color: pickColorFromString(domain || companyName),
        analysisType,
        url: normalized,
        industryLabel,
        industryId: indId,
        messages: [],
      };

      setChats((prev) => [newChat, ...prev]);
      setActiveChatId(chatId);

      queueMicrotask(() => {
        pushMessage(chatId, userMsg);
        pushMessage(chatId, assistantMsg);

        runAnalysisPipelineAndRender(chatId, payload, assistantMsgId).catch((e: any) => {
          updateMessage(chatId, assistantMsgId, `❌ Error al analizar: ${e?.message ?? "Error desconocido"}`);
        });
      });
    } else {
      const chatId = activeChatId;

      // update header info if it was placeholder
      setChats((prev) =>
        prev.map((c) =>
          c.id === chatId && (c.companyName === "Nuevo chat" || !c.companyName)
            ? {
                ...c,
                companyName,
                domain,
                initial: (companyName[0] || "?").toUpperCase(),
                color: pickColorFromString(domain || companyName),
                analysisType,
                url: normalized,
                industryLabel,
                industryId: indId,
                whenISO: nowISO,
              }
            : c
        )
      );

      pushMessage(chatId, userMsg);
      pushMessage(chatId, assistantMsg);

      runAnalysisPipelineAndRender(chatId, payload, assistantMsgId).catch((e: any) => {
        updateMessage(chatId, assistantMsgId, `❌ Error al analizar: ${e?.message ?? "Error desconocido"}`);
      });
    }

    // reset inputs
    setUrlInput("");
    setCompanyNameInput("");
    setIndustryLabel("");
    setUrlError(null);
    setCompanyError(null);
    setIndustryError(null);
    setPopupOpen(false);

    requestAnimationFrame(() => urlRef.current?.focus());
  };

  return (
    <AppShell>
      <div className="flex h-[calc(100dvh-140px)] gap-6">
        {/* Sidebar / Historial */}
        <section
          className={[
            "shrink-0 rounded-2xl border border-border bg-app shadow-sm h-full flex flex-col min-h-0 transition-all duration-300",
            sidebarCollapsed ? "w-[96px]" : "w-[360px]",
          ].join(" ")}
        >
          {/* Header */}
          <div
            className={[
              "border-b border-border",
              sidebarCollapsed ? "px-2 py-3" : "px-5 py-4",
            ].join(" ")}
          >
            {!sidebarCollapsed ? (
              <>
                <div className="flex items-center justify-between">
                  <div className="text-lg font-semibold">Historial de análisis</div>
                  <button
                    type="button"
                    onClick={() => setSidebarCollapsed(true)}
                    className="grid h-10 w-10 place-items-center rounded-xl border border-border bg-card text-text-secondary hover:bg-hover"
                    aria-label="Minimizar"
                    title="Minimizar"
                  >
                    <PanelLeft size={18} />
                  </button>
                </div>

                <div className="mt-4 flex items-center gap-2">
                  <button
                    type="button"
                    onClick={handleNewChat}
                    className="inline-flex items-center gap-2 rounded-2xl border border-border bg-card px-3 py-2 text-sm font-semibold text-text-primary hover:bg-hover"
                  >
                    <span className="grid h-6 w-6 place-items-center rounded-lg border border-border bg-app">
                      <Plus size={16} />
                    </span>
                    Nuevo chat
                  </button>
                </div>

                <div className="mt-3 flex items-center gap-2 rounded-2xl border border-border bg-card px-3 py-2">
                  <span className="text-text-muted">
                    <Search size={16} />
                  </span>
                  <input
                    placeholder="Buscar cuenta..."
                    className="w-full bg-transparent text-sm text-text-primary placeholder:text-text-muted outline-none"
                  />
                </div>
              </>
            ) : (
              <div className="flex flex-col items-center gap-3">
                <button
                  type="button"
                  onClick={() => setSidebarCollapsed(false)}
                  className="icon-btn h-10 w-10 rounded-xl border border-border bg-card text-text-secondary hover:bg-hover"
                  aria-label="Expandir"
                  title="Expandir"
                >
                  <PanelRight className="h-[18px] w-[18px] shrink-0" />
                </button>

                <button
                  type="button"
                  onClick={handleNewChat}
                  className="icon-btn h-10 w-10 rounded-xl border border-border bg-card text-text-secondary hover:bg-hover"
                  aria-label="Nuevo chat"
                  title="Nuevo chat"
                >
                  <Plus className="h-[18px] w-[18px] shrink-0" />
                </button>
              </div>
            )}
          </div>

          {/* Lista de chats */}
          <div className="min-h-0 flex-1 overflow-auto px-2 py-3">
            {chats.map((h) => {
              const selected = h.id === activeChatId;

              if (sidebarCollapsed) {
                return (
                  <button
                    key={h.id}
                    onClick={() => setActiveChatId(h.id)}
                    className={[
                      "mx-auto mb-3 inline-flex aspect-square",
                      "!h-16 !w-16 items-center justify-center rounded-full border transition overflow-hidden",
                      selected ? "border-brand bg-brand-accent" : "border-border bg-card hover:bg-hover",
                    ].join(" ")}
                    title={`${h.companyName} • ${h.analysisType}${h.domain ? ` • ${h.domain}` : ""}`}
                    style={{ width: 64, height: 64 }}
                  >
                    <span
                      className={[
                        "inline-flex aspect-square !h-11 !w-11 items-center justify-center rounded-full",
                        "text-base font-bold text-white leading-none",
                        h.color,
                      ].join(" ")}
                      style={{ width: 44, height: 44 }}
                    >
                      {h.initial}
                    </span>
                  </button>
                );
              }

              return (
                <button
                  key={h.id}
                  onClick={() => setActiveChatId(h.id)}
                  className={[
                    "flex w-full items-center gap-4 rounded-2xl border px-4 py-4 text-left shadow-sm transition",
                    selected ? "border-brand bg-brand-accent" : "border-border bg-card hover:bg-hover",
                  ].join(" ")}
                  title={`${h.companyName} • ${h.analysisType}${h.domain ? ` • ${h.domain}` : ""}`}
                >
                  <div
                    className={[
                      "flex h-11 w-11 items-center justify-center rounded-full text-sm font-bold text-white",
                      h.color,
                    ].join(" ")}
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
              );
            })}
          </div>
        </section>

        {/* Chat */}
        <section className="min-w-0 flex-1 rounded-2xl border border-border bg-app shadow-sm h-full flex flex-col min-h-0 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-border px-6 py-4 shrink-0">
            <div className="flex items-center gap-3">
              <div className="grid h-10 w-10 place-items-center rounded-full bg-brand text-white">
                <Zap size={18} />
              </div>
              <div className="leading-tight">
                <div className="flex items-center gap-2">
                  <div className="text-sm font-semibold">HPE Insight AI</div>
                  <span className="h-2 w-2 rounded-full bg-success" />
                </div>
                <div className="text-xs text-text-secondary">Asistente estratégico de cuentas</div>
              </div>
            </div>

            <button className="icon-btn h-10 w-10 rounded-xl border border-border bg-card text-text-secondary hover:bg-hover">
              <MoreHorizontal className="h-[18px] w-[18px] shrink-0" />
            </button>
          </div>

          <div className="relative flex flex-1 min-h-0 flex-col">
            {/* Scroll area */}
            <div className="min-h-0 flex-1 overflow-auto px-8 py-8 pb-44">
              {!activeChat ? (
                <div className="flex h-full flex-col items-center justify-center text-center">
                  <h2 className="text-3xl font-semibold tracking-tight">¿Con qué cuenta quieres comenzar?</h2>
                  <p className="mt-2 text-sm text-text-secondary">
                    Ingresa URL, nombre e industria para iniciar el análisis.
                  </p>
                </div>
              ) : activeChat.messages.length === 0 ? (
                <div className="flex h-full flex-col items-center justify-center text-center">
                  <h2 className="text-2xl font-semibold tracking-tight">Nuevo chat</h2>
                  <p className="mt-2 text-sm text-text-secondary">
                    Ingresa URL, nombre e industria para iniciar el análisis.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {activeChat.messages.map((m) =>
                    m.role === "assistant" ? (
                      <AssistantBubble key={m.id} text={m.text} />
                    ) : (
                      <UserBubble key={m.id} text={m.text} />
                    )
                  )}
                </div>
              )}
            </div>

            {/* Composer */}
            <div className="z-20 w-full sticky bottom-0 border-t border-border bg-app px-8 py-5">
              <Composer
                urlValue={urlInput}
                setUrlValue={setUrlInput}
                companyName={companyNameInput}
                setCompanyName={setCompanyNameInput}
                industryLabel={industryLabel}
                setIndustryLabel={setIndustryLabel}
                urlError={urlError}
                companyError={companyError}
                industryError={industryError}
                setUrlError={setUrlError}
                setCompanyError={setCompanyError}
                setIndustryError={setIndustryError}
                popupOpen={popupOpen}
                setPopupOpen={setPopupOpen}
                analysisType={analysisType}
                setAnalysisType={setAnalysisType}
                popupRef={popupRef}
                plusBtnRef={plusBtnRef}
                onSend={handleSend}
                canSend={canSend}
                urlRef={urlRef}
                companyRef={companyRef}
              />
            </div>
          </div>
        </section>
      </div>
    </AppShell>
  );
}

/* ---------- UI helpers ---------- */

function AssistantBubble({ text }: { text: string }) {
  return (
    <div
      className={[
        "max-w-[760px] rounded-2xl bg-card px-4 py-3 text-sm text-text-primary border border-border",
        "whitespace-pre-wrap break-words overflow-hidden",
        "[overflow-wrap:anywhere] [word-break:break-word]",
      ].join(" ")}
    >
      {text}
    </div>
  );
}

function UserBubble({ text }: { text: string }) {
  const shown = truncateIfUrl(text, 110);

  return (
    <div className="flex w-full justify-end">
      <div
        className={[
          "max-w-[760px] rounded-2xl bg-brand-accent px-4 py-3 text-sm text-text-primary border border-border",
          "whitespace-pre-wrap break-words overflow-hidden",
          "[overflow-wrap:anywhere] [word-break:break-word]",
        ].join(" ")}
        title={text}
      >
        {shown}
      </div>
    </div>
  );
}

function Composer({
  urlValue,
  setUrlValue,
  companyName,
  setCompanyName,
  industryLabel,
  setIndustryLabel,
  urlError,
  companyError,
  industryError,
  setUrlError,
  setCompanyError,
  setIndustryError,
  popupOpen,
  setPopupOpen,
  analysisType,
  setAnalysisType,
  popupRef,
  plusBtnRef,
  onSend,
  canSend,
  urlRef,
  companyRef,
}: {
  urlValue: string;
  setUrlValue: Dispatch<SetStateAction<string>>;
  companyName: string;
  setCompanyName: Dispatch<SetStateAction<string>>;
  industryLabel: string;
  setIndustryLabel: Dispatch<SetStateAction<string>>;
  urlError: string | null;
  companyError: string | null;
  industryError: string | null;
  setUrlError: Dispatch<SetStateAction<string | null>>;
  setCompanyError: Dispatch<SetStateAction<string | null>>;
  setIndustryError: Dispatch<SetStateAction<string | null>>;
  popupOpen: boolean;
  setPopupOpen: Dispatch<SetStateAction<boolean>>;
  analysisType: string;
  setAnalysisType: Dispatch<SetStateAction<string>>;
  popupRef: RefObject<HTMLDivElement | null>;
  plusBtnRef: RefObject<HTMLButtonElement | null>;
  onSend: () => void;
  canSend: boolean;
  urlRef: RefObject<HTMLInputElement | null>;
  companyRef: RefObject<HTMLInputElement | null>;
}) {
  const options = [
    "Análisis Completo",
    "Detectar Oportunidades",
    "Mapear Stack Actual",
    "Analizar Madurez Digital",
  ];

  return (
    <div className="relative">
      <div className="flex flex-col gap-3">
        {/* Row 1: URL + plus (analysis type) + send */}
        <div className="flex items-center gap-3 rounded-2xl border border-border bg-card px-3 py-3">
          <div className="relative">
            <button
              ref={plusBtnRef}
              type="button"
              onClick={() => setPopupOpen((v) => !v)}
              className="icon-btn h-10 w-10 rounded-xl border border-border bg-app text-text-secondary hover:bg-hover"
              aria-label="Opciones"
            >
              <Plus className="h-[18px] w-[18px] shrink-0" />
            </button>

            {popupOpen && (
              <div
                ref={popupRef}
                className={[
                  "absolute left-0 z-50 bottom-12",
                  "w-[min(760px,calc(100vw-32px))] sm:w-[min(760px,calc(100vw-64px))]",
                ].join(" ")}
              >
                <div className="w-full rounded-2xl border border-border bg-app p-3 shadow-xl max-h-[320px] overflow-auto">
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
                            setPopupOpen(false);
                            requestAnimationFrame(() => urlRef.current?.focus());
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
                              <Check size={16} />
                            </span>
                          ) : (
                            <span className="h-6 w-6" />
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>

          <input
            ref={urlRef}
            value={urlValue}
            onChange={(e) => {
              const next = e.target.value;
              setUrlValue(next);
              const trimmed = next.trim();
              if (!trimmed) setUrlError(null);
              else {
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
            placeholder="URL del sitio web (obligatorio) — ej: https://empresa.com"
            className={[
              "h-10 min-w-0 flex-1 bg-transparent text-sm outline-none",
              "text-text-primary placeholder:text-text-muted",
            ].join(" ")}
          />

          <button
            type="button"
            onClick={onSend}
            disabled={!canSend}
            className={[
              "icon-btn h-10 w-10 rounded-full text-white",
              canSend ? "bg-brand hover:bg-brand-dark" : "bg-border cursor-not-allowed",
            ].join(" ")}
            aria-label="Enviar"
          >
            <ArrowUp className="h-[18px] w-[18px] shrink-0" />
          </button>
        </div>

        {/* Row 2: Name + Industry */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div>
            <label className="mb-1 block text-xs font-semibold text-text-muted">Nombre de la empresa (obligatorio)</label>
            <input
              ref={companyRef}
              value={companyName}
              onChange={(e) => {
                const v = e.target.value;
                setCompanyName(v);
                setCompanyError(v.trim() ? null : "El nombre de la empresa es obligatorio.");
              }}
              placeholder="Ej. KIA"
              className={[
                "h-11 w-full rounded-2xl border border-border bg-card px-4 text-sm outline-none",
                "text-text-primary placeholder:text-text-muted",
                companyError ? "border-error" : "focus:border-brand",
              ].join(" ")}
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-semibold text-text-muted">Industria (obligatoria)</label>
            <div className="relative">
              <select
                value={industryLabel}
                onChange={(e) => {
                  setIndustryLabel(e.target.value);
                  setIndustryError(e.target.value ? null : "Selecciona una industria.");
                }}
                className={[
                  "h-11 w-full appearance-none rounded-2xl border border-border bg-card px-4 pr-10 text-sm outline-none",
                  "text-text-primary",
                  industryError ? "border-error" : "focus:border-brand",
                ].join(" ")}
              >
                <option value="">Selecciona la industria</option>
                {INDUSTRIES.map((i) => (
                  <option key={i} value={i}>
                    {i}
                  </option>
                ))}
              </select>

              <span className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-text-muted">
                <ChevronDown size={18} />
              </span>
            </div>
          </div>
        </div>

        {/* Errors */}
        {urlValue.trim().length > 0 && urlError && (
          <div className="rounded-xl border border-border bg-card px-3 py-2 text-xs text-text-secondary">
            <span className="font-semibold text-text-primary">URL inválida:</span> {urlError}
          </div>
        )}

        {companyError && (
          <div className="rounded-xl border border-border bg-card px-3 py-2 text-xs text-text-secondary">
            <span className="font-semibold text-text-primary">Nombre inválido:</span> {companyError}
          </div>
        )}

        {industryError && (
          <div className="rounded-xl border border-border bg-card px-3 py-2 text-xs text-text-secondary">
            <span className="font-semibold text-text-primary">Industria inválida:</span> {industryError}
          </div>
        )}

        <div className="flex items-center justify-between px-1 text-xs text-text-secondary">
          <span>
            Selección actual: <span className="font-semibold text-text-primary">{analysisType}</span>
          </span>

          <span className="inline-flex items-center gap-1">
            <Zap size={14} /> Insight AI
          </span>
        </div>
      </div>
    </div>
  );
}