import Navbar from "@/components/Navbar";
import Sidebar, { MobileNav } from "@/components/Sidebar";

export default function AppLayout({ title, description, actions, children }) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(28,85,63,0.08),_transparent_28%),linear-gradient(180deg,#f6f9f6_0%,#f2f7f3_100%)]">
      <Navbar />
      <div className="mx-auto flex max-w-[1800px] gap-4 px-3 pb-10 pt-4 sm:px-4 lg:px-6">
        <Sidebar />
        <div className="min-w-0 flex-1">
          <MobileNav />
          <main className="mx-auto w-full max-w-7xl px-1 py-6 sm:px-2 lg:py-8">
            {(title || actions) && (
              <div className="glass-panel mb-6 flex flex-wrap items-end justify-between gap-4 rounded-[24px] px-5 py-4">
                <div>
                  {title && <h1 className="font-display text-2xl text-deep sm:text-3xl">{title}</h1>}
                  {description && (
                    <p className="mt-1 max-w-2xl text-sm text-muted-foreground">{description}</p>
                  )}
                </div>
                {actions}
              </div>
            )}
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
