import { useEffect, useMemo, useState } from "react";
import {
  Bell,
  ChevronDown,
  LogOut,
  Menu,
  Search,
  X,
} from "lucide-react";

import SearchBar from "@/components/SearchBar";
import { useProjectData } from "@/context/ProjectDataContext";
import { useSidebar } from "@/hooks/useSidebar";
import { Link, useNavigate } from "@/lib/navigation";
import { useAuth } from "@/lib/auth";

const links = [
  { label: "Home", to: "/" },
  { label: "Dashboard", to: "/dashboard" },
  { label: "About", to: "/", hash: "about" },
  { label: "Map", to: "/risk-map" },
];

export default function Navbar() {
  const { open, toggle } = useSidebar();
  const { warnings = [] } = useProjectData();
  const navigate = useNavigate();
  const { isAuthenticated, user, signOut } = useAuth();

  const [scrolled, setScrolled] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);

    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const liveWarnings = useMemo(
    () => warnings.slice(0, 3),
    [warnings]
  );

  const handleLogout = () => {
    signOut();
    setProfileOpen(false);
    navigate("/");
  };

  return (
   <header className="sticky top-0 z-[1100] w-full px-3 pt-3 sm:px-4 lg:px-6">
  <div className="mx-auto flex min-h-[60px] w-full items-center rounded-2xl border border-white/60 bg-white/55 px-4 shadow-lg backdrop-blur-xl">

        {/* SIDEBAR TOGGLE */}
        <button
          onClick={toggle}
          aria-label={open ? "Close navigation" : "Open navigation"}
          aria-expanded={open}
          className="mr-2 grid h-8 w-8 shrink-0 place-items-center rounded-full border border-forest/10 bg-white/70 text-deep shadow-sm transition-all hover:bg-sage-soft hover:shadow-md"
        >
          {open ? (
            <X className="h-4 w-4" />
          ) : (
            <Menu className="h-4 w-4" />
          )}
        </button>

        {/* BRAND */}
        <Link to="/" className="flex shrink-0 items-center gap-2">
          <div className="grid h-9 w-9 shrink-0 place-items-center overflow-hidden rounded-lg bg-forest/95 shadow-sm ring-1 ring-forest/20">
            <img
              src="/logo.png"
              alt="SlopeShield"
              className="h-full w-full object-contain scale-[1.6]"

            />
          </div>

          <span className="hidden text-[14px] font-semibold tracking-tight text-deep sm:block">
            SlopeShield
          </span>
        </Link>

        {/* NAVIGATION */}
        <nav className="ml-5 hidden items-center gap-0.5 md:flex">
          {links.map((link) => {
            const isDashboard =
              link.to === "/dashboard" &&
              window.location.pathname === "/dashboard";

            return (
              <Link
                key={link.label}
                to={link.to}
                hash={link.hash}
                className={`relative rounded-lg px-3 py-1.5 text-[13px] font-medium transition-all duration-200 ${
                  isDashboard
                    ? "text-deep"
                    : "text-muted-foreground hover:bg-sage-soft/70 hover:text-deep"
                }`}
              >
                {link.label}

                {isDashboard && (
                  <span className="absolute bottom-0.5 left-1/2 h-0.5 w-4 -translate-x-1/2 rounded-full bg-forest" />
                )}
              </Link>
            );
          })}
        </nav>

        {/* RIGHT ACTIONS */}
        <div className="ml-auto flex items-center gap-1.5">

          {/* SEARCH */}
          <div className="hidden lg:block">
            <div className="w-[190px] xl:w-[220px]">
              <SearchBar />
            </div>
          </div>

          <button
            onClick={() => setSearchOpen((value) => !value)}
            aria-label="Toggle search"
            className="grid h-8 w-8 place-items-center rounded-full border border-forest/10 bg-white/70 text-deep shadow-sm transition-all hover:bg-sage-soft hover:shadow-md lg:hidden"
          >
            <Search className="h-4 w-4" />
          </button>

          {/* NOTIFICATIONS */}
          <div className="relative">
            <button
              onClick={() =>
                setNotificationsOpen((value) => !value)
              }
              aria-label="Toggle notifications"
              aria-expanded={notificationsOpen}
              className="relative grid h-8 w-8 place-items-center rounded-full border border-forest/10 bg-white/70 text-deep shadow-sm transition-all hover:bg-sage-soft hover:shadow-md"
            >
              <Bell className="h-4 w-4" />

              {liveWarnings.length > 0 && (
                <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-risk-high ring-1 ring-white" />
              )}
            </button>

            {notificationsOpen && (
              <div className="absolute right-0 top-[calc(100%+10px)] z-[1200] w-72 rounded-2xl border border-white/80 bg-white/95 p-3 shadow-xl backdrop-blur-xl">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                  Monitoring Updates
                </p>

                <p className="mt-1 text-sm font-semibold text-deep">
                  Notifications
                </p>

                <div className="mt-2 space-y-2">
                  {liveWarnings.map((warning) => (
                    <Link
                      key={warning.id}
                      to={`/location/${warning.locationId}`}
                      onClick={() => setNotificationsOpen(false)}
                      className="block rounded-xl p-2.5 hover:bg-sage-soft/50"
                    >
                      <p className="text-sm font-medium">
                        {warning.location.split(",")[0]}
                      </p>

                      <p className="mt-1 text-[11px] text-muted-foreground">
                        Rainfall {warning.rainfall} mm · Probability{" "}
                        {warning.probability}%
                      </p>
                    </Link>
                  ))}

                  {liveWarnings.length === 0 && (
                    <p className="py-4 text-center text-xs text-muted-foreground">
                      No active warnings.
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* PROFILE */}
          <div className="relative">
            <button
              onClick={() => setProfileOpen((value) => !value)}
              aria-label="Open profile"
              aria-expanded={profileOpen}
              className="flex h-8 items-center gap-1.5 rounded-full border border-forest/10 bg-white/70 px-1 pr-2 text-sm shadow-sm transition-all hover:bg-sage-soft hover:shadow-md"
            >
              <span className="grid h-6 w-6 place-items-center rounded-full bg-sage-soft text-[10px] font-semibold text-deep">
                {isAuthenticated && user?.name
                  ? user.name.trim().charAt(0).toUpperCase()
                  : "G"}
              </span>

              <span className="hidden max-w-[75px] truncate text-xs font-medium text-deep sm:block">
                {isAuthenticated && user?.name
                  ? user.name.split(" ")[0]
                  : "Guest"}
              </span>

              <ChevronDown className="h-3 w-3 text-muted-foreground" />
            </button>

            {profileOpen && (
              <div className="absolute right-0 top-[calc(100%+10px)] z-[1200] w-48 rounded-2xl border border-white/80 bg-white/95 p-2 shadow-xl backdrop-blur-xl">
                <div className="border-b border-slate-200/70 px-2 pb-2">
                  <p className="truncate text-sm font-semibold text-deep">
                    {isAuthenticated && user?.name
                      ? user.name
                      : "Guest user"}
                  </p>
                </div>

                <Link
                  to="/settings"
                  onClick={() => setProfileOpen(false)}
                  className="mt-1 block rounded-xl px-2 py-2 text-sm hover:bg-sage-soft/60"
                >
                  Settings
                </Link>

                {isAuthenticated ? (
                  <button
                    onClick={handleLogout}
                    className="flex w-full items-center gap-2 rounded-xl px-2 py-2 text-left text-sm hover:bg-sage-soft/60"
                  >
                    <LogOut className="h-3.5 w-3.5" />
                    Log out
                  </button>
                ) : (
                  <Link
                    to="/login"
                    onClick={() => setProfileOpen(false)}
                    className="block rounded-xl px-2 py-2 text-sm hover:bg-sage-soft/60"
                  >
                    Sign In
                  </Link>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* MOBILE SEARCH */}
      {searchOpen && (
        <div className="border-t border-white/60 bg-white/90 px-3 py-2 backdrop-blur-xl lg:hidden">
          <SearchBar placeholder="Search location" />
        </div>
      )}
    </header>
  );
}