import React, { useEffect, useMemo, useState } from "react";

type NavItem = { key: string; label: string; icon: React.ReactNode; active?: boolean };

const nav: NavItem[] = [
  { key: "daily", label: "Análisis Diario", icon: <GridIcon /> },
  { key: "accounts", label: "Cuentas", icon: <TableIcon /> },
  { key: "insights", label: "Insights", icon: <BulbIcon /> },
  { key: "profile360", label: "Perfil de Cuenta 360°", icon: <Circle360Icon />, active: true },
  { key: "recs", label: "Recomendaciones", icon: <MailIcon /> },
  { key: "history", label: "Historial del Analisis", icon: <ClockIcon /> },
];

const settingsNav: NavItem[] = [
  { key: "config", label: "Configuración", icon: <GearIcon /> },
  { key: "profile", label: "Mi Perfil", icon: <UserIcon /> },
];

type AppShellProps = {
  activeKey?: string; // para marcar item activo por pantalla
  children: React.ReactNode;
};

export default function AppShell({ activeKey, children }: AppShellProps) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const root = document.documentElement;
    setIsDark(root.classList.contains("dark"));
  }, []);

  const toggleTheme = () => {
    const root = document.documentElement;
    root.classList.toggle("dark");
    setIsDark(root.classList.contains("dark"));
  };

  const computedNav = useMemo(() => {
    if (!activeKey) return nav;
    return nav.map((i) => ({ ...i, active: i.key === activeKey }));
  }, [activeKey]);

  return (
    <div className="min-h-dvh bg-page text-text-primary">
      {/* Overlay mobile */}
      {mobileOpen && (
        <button
          aria-label="Cerrar menú"
          className="fixed inset-0 z-40 bg-black/30 lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      <div className="flex min-h-dvh">
        {/* Sidebar Desktop */}
        <aside className="hidden lg:flex fixed left-0 top-0 z-50 h-dvh w-72 flex-col border-r border-border bg-app overflow-hidden">
          <Sidebar navItems={computedNav} onClose={undefined} />
        </aside>

        {/* Sidebar Mobile */}
        <aside
          className={[
            "lg:hidden fixed left-0 top-0 z-50 h-dvh w-72 border-r border-border bg-app overflow-hidden",
            "transition-transform duration-200",
            mobileOpen ? "translate-x-0" : "-translate-x-full",
          ].join(" ")}
        >
          <Sidebar navItems={computedNav} onClose={() => setMobileOpen(false)} />
        </aside>

        {/* CONTENT */}
        <div className="flex-1 lg:pl-72">
          <div className="h-dvh overflow-y-auto">
            {/* Topbar */}
            <div className="sticky top-0 z-30 bg-page/90 backdrop-blur">
              <div className="flex w-full items-center gap-3 px-4 py-4 lg:px-8">
                <button
                  className="grid h-11 w-11 place-items-center rounded-xl border border-border bg-app text-text-secondary lg:hidden"
                  onClick={() => setMobileOpen(true)}
                  aria-label="Abrir menú"
                >
                  <HamburgerIcon />
                </button>

                <div className="flex-1">
                  <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted">
                      <SearchIcon />
                    </span>
                    <input
                      className="h-11 w-full rounded-2xl border border-border bg-app pl-11 pr-4 text-sm text-text-primary placeholder:text-text-muted outline-none focus:border-brand focus:ring-2 focus:ring-brand/20"
                      placeholder="Buscar..."
                    />
                  </div>
                </div>

                <div className="hidden items-center gap-2 sm:flex">
                  <IconButton title={isDark ? "Modo Light" : "Modo Dark"} onClick={toggleTheme}>
                    <ThemeIcon />
                  </IconButton>
                  <IconButton title="Notificaciones">
                    <BellIcon />
                  </IconButton>
                  <IconButton title="Ajustes">
                    <GearIcon />
                  </IconButton>
                  <div className="mx-2 hidden h-8 w-px bg-border md:block" />
                  <div className="h-10 w-10 overflow-hidden rounded-full border border-border bg-app" />
                </div>
              </div>
            </div>

            {/* Page content */}
            <main className="w-full px-4 pb-10 pt-2 lg:px-8">
              <div className="mx-auto w-full max-w-[1680px]">{children}</div>
            </main>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ---------------- Sidebar ---------------- */

function Sidebar({ onClose, navItems }: { onClose?: () => void; navItems: NavItem[] }) {
  return (
    <div className="flex h-full flex-col">
      <div className="px-6 pt-6 pb-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <div className="text-4xl font-black tracking-tight">
              {/* Ajusta a tu ruta real de logo */}
              <img src="src/assets/brand/logo_HPE.png" alt="Logo" className="h-10 w-auto" />
            </div>
            <div className="mt-1 text-xs font-semibold text-text-secondary">Account Intelligence</div>
          </div>

          {onClose && (
            <button
              onClick={onClose}
              className="mt-1 grid h-10 w-10 place-items-center rounded-xl border border-border bg-app text-text-secondary lg:hidden"
              aria-label="Cerrar menú"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      <div className="px-4">
        <div className="text-[11px] font-semibold text-text-muted">DASHBOARD</div>
        <nav className="mt-3 space-y-1">
          {navItems.map((i) => (
            <SideItem key={i.key} label={i.label} icon={i.icon} active={i.active} />
          ))}
        </nav>
      </div>

      <div className="mt-auto px-4 pb-6">
        <div className="mt-10 text-[11px] font-semibold text-text-muted">CONFIGURACIONES</div>
        <nav className="mt-3 space-y-1">
          {settingsNav.map((i) => (
            <SideItem key={i.key} label={i.label} icon={i.icon} />
          ))}
        </nav>
      </div>
    </div>
  );
}

function SideItem({ icon, label, active }: { icon: React.ReactNode; label: string; active?: boolean }) {
  return (
    <a
      href="#"
      className={[
        "no-underline flex items-center gap-3 rounded-2xl px-3 py-3 text-sm font-medium transition",
        active ? "bg-brand-accent text-text-primary" : "text-text-secondary hover:bg-hover hover:text-text-primary",
      ].join(" ")}
    >
      <span className="grid h-10 w-10 place-items-center rounded-2xl border border-border bg-card text-text-secondary">
        {icon}
      </span>
      <span className="truncate">{label}</span>
    </a>
  );
}

/* ---------------- UI components ---------------- */

function IconButton({
  children,
  title,
  onClick,
}: {
  children: React.ReactNode;
  title: string;
  onClick?: () => void;
}) {
  return (
    <button
      title={title}
      onClick={onClick}
      className="grid h-11 w-11 place-items-center rounded-xl border border-border bg-app text-text-secondary hover:bg-hover active:translate-y-px"
    >
      {children}
    </button>
  );
}

/* ---------------- Icons (copiados del Dashboard) ---------------- */

function HamburgerIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
      <path d="M4 6h16v2H4V6Zm0 5h16v2H4v-2Zm0 5h16v2H4v-2Z" fill="currentColor" />
    </svg>
  );
}
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
function ThemeIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path
        d="M12 18a6 6 0 1 0 0-12 6 6 0 0 0 0 12Zm0-16h2v3h-2V2ZM12 19h2v3h-2v-3ZM2 12h3v2H2v-2Zm17 0h3v2h-3v-2Z"
        fill="currentColor"
      />
    </svg>
  );
}
function BellIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path
        d="M12 22a2.5 2.5 0 0 0 2.45-2h-4.9A2.5 2.5 0 0 0 12 22Zm7-6V11a7 7 0 0 0-5-6.7V3a2 2 0 1 0-4 0v1.3A7 7 0 0 0 5 11v5l-2 2v1h20v-1l-2-2Z"
        fill="currentColor"
      />
    </svg>
  );
}
function GearIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
      <path
        d="M19.14 12.94c.04-.31.06-.62.06-.94s-.02-.63-.06-.94l2.03-1.58a.6.6 0 0 0 .14-.77l-1.92-3.32a.6.6 0 0 0-.73-.26l-2.39.96a7.8 7.8 0 0 0-1.63-.94l-.36-2.54A.6.6 0 0 0 13.7 1h-3.4a.6.6 0 0 0-.59.5l-.36 2.54c-.58.22-1.12.52-1.63.94l-2.39-.96a.6.6 0 0 0-.73.26L1.68 7.7a.6.6 0 0 0 .14.77l2.03 1.58c-.04.31-.06.62-.06.94s.02.63.06.94L1.82 14.52a.6.6 0 0 0-.14.77l1.92 3.32c.16.28.5.39.8.26l2.39-.96c.5.41 1.05.72 1.63.94l.36 2.54c.05.29.3.5.59.5h3.4c.29 0 .54-.21.59-.5l.36-2.54c.58-.22 1.12-.52 1.63-.94l2.39.96c.3.12.64.02.8-.26l1.92-3.32a.6.6 0 0 0-.14-.77l-2.03-1.58ZM12 15.5A3.5 3.5 0 1 1 12 8a3.5 3.5 0 0 1 0 7.5Z"
        fill="currentColor"
      />
    </svg>
  );
}

function GridIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-brand">
      <path d="M4 4h7v7H4V4Zm9 0h7v7h-7V4ZM4 13h7v7H4v-7Zm9 0h7v7h-7v-7Z" fill="currentColor" />
    </svg>
  );
}
function TableIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-text-secondary">
      <path
        d="M4 5h16a2 2 0 0 1 2 2v2H2V7a2 2 0 0 1 2-2Zm-2 6h20v6H2v-6Zm0 8h20v1a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-1Z"
        fill="currentColor"
      />
    </svg>
  );
}
function BulbIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-text-secondary">
      <path d="M9 21h6v-1H9v1Zm3-20a7 7 0 0 0-4 12.74V17a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2v-3.26A7 7 0 0 0 12 1Z" fill="currentColor" />
    </svg>
  );
}
function Circle360Icon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-text-secondary">
      <path d="M12 2a10 10 0 1 0 9.95 11H19l3.5-3.5L26 13h-2.05A12 12 0 1 1 12 0v2Z" fill="currentColor" />
    </svg>
  );
}
function MailIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-text-secondary">
      <path d="M4 6h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2Zm0 2 8 5 8-5H4Z" fill="currentColor" />
    </svg>
  );
}
function ClockIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-text-secondary">
      <path d="M12 2a10 10 0 1 0 .001 20.001A10 10 0 0 0 12 2Zm1 5h-2v6l5 3 1-1.73-4-2.27V7Z" fill="currentColor" />
    </svg>
  );
}
function UserIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="text-text-secondary">
      <path d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.42 0-8 2-8 4.5V21h16v-2.5C20 16 16.42 14 12 14Z" fill="currentColor" />
    </svg>
  );
}