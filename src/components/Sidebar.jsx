import { Link, useLocation } from "@/lib/navigation";
import { AlertTriangle, BarChart3, FileText, LayoutDashboard, Map, Settings, UserRound } from "lucide-react";

import Logo from "@/components/Logo";
import { useSidebar } from "@/hooks/useSidebar";
import { useAuth } from "@/lib/auth";

const items = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/risk-map", label: "Risk Map", icon: Map },
  { to: "/alerts", label: "Early Warnings", icon: AlertTriangle },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/settings", label: "Settings", icon: Settings },
];

export default function Sidebar() {
  const { open } = useSidebar();
  const location = useLocation();
  const { user } = useAuth();
  const displayName = user?.name || "User";

  return (
    <aside
      className={`sticky top-20 hidden h-[calc(100vh-5rem)] shrink-0 overflow-hidden transition-[width,opacity] duration-300 md:flex md:flex-col ${
       open ? "w-60 opacity-100" : "w-0 opacity-0"
  }`}
  aria-hidden={!open}
>
      <div className="glass-panel mb-3 mt-0 h-full w-60 overflow-hidden rounded-[26px] p-2 shadow-[0_18px_48px_rgba(27,46,36,0.09)]">
        <div className="flex h-16 items-center border-b border-white/60 px-3">
          <Logo to="/dashboard" />
        </div>

        <nav className="flex-1 space-y-1 p-2 pt-3">
          {items.map(({ to, label, icon: Icon }) => {
            const active = location.pathname === to;
            return (
              <Link
                key={to}
                to={to}
                title={label}
                className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-all ${
                  active
                    ? "bg-sage-soft text-deep shadow-sm ring-1 ring-forest/10"
                    : "text-muted-foreground hover:bg-white/60 hover:text-foreground"
                }`}
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span className="truncate">{label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-white/60 p-3">
          <div className="flex items-center gap-3">
            <span className="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-sage-soft text-xs font-semibold text-deep">
              {displayName.charAt(0).toUpperCase() || <UserRound className="h-3.5 w-3.5" />}
            </span>
            <span className="min-w-0 leading-tight">
            <span className="block truncate text-sm font-medium text-deep">{displayName}</span>
            <span className="block truncate text-xs text-muted-foreground">Hidden Variables</span>
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}

export function MobileNav() {
  return (
    <nav className="sticky top-[7.5rem] z-[900] flex gap-1 overflow-x-auto border-b border-white/60 bg-white/35 px-3 py-2 backdrop-blur-sm md:hidden">
      {items.map(({ to, label, icon: Icon }) => (
        <Link
          key={to}
          to={to}
          className="flex shrink-0 items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs text-muted-foreground"
        >
          <Icon className="h-3.5 w-3.5" />
          {label}
        </Link>
      ))}
    </nav>
  );
}
