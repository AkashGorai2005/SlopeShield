import { useNavigate } from "@/lib/navigation";
import { useAuth } from "@/lib/auth";
import { useState } from "react";

import Logo from "@/components/Logo";
import { login } from "@/services/api";

export default function Login() {
  const navigate = useNavigate();
  const { signIn } = useAuth();
  const [form, setForm] = useState({ name: "", email: "" });

  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    const name = form.name.trim() || "User";
    const email = form.email.trim() || "user@SLOPESHIELD.local";
    try {
      const user = await login(name, email);
      signIn(user);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message || "Backend is unavailable. Start the API on port 8000.");
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top,_rgba(148,163,184,0.18),_transparent_32%),linear-gradient(135deg,#f5f8f5_0%,#eef5f1_26%,#f9faf7_100%)]">
      <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1600&q=80')] bg-cover bg-center opacity-20" />
      <div className="absolute inset-0 bg-gradient-to-r from-white/55 via-white/15 to-white/55" />

      <div className="relative z-10 grid min-h-screen place-items-center px-4 py-12">
        <div className="glass-panel w-full max-w-md rounded-[28px] p-6 sm:p-8">
          <div className="flex items-center justify-between">
            <Logo />
          </div>

          <div className="mt-8">
            <p className="eyebrow">Welcome</p>
            <h1 className="mt-2 text-3xl text-deep">Welcome to SLOPESHIELD NER</h1>
            <p className="mt-2 text-sm text-muted-foreground">
              Monitor landslide risk. Understand your surroundings.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <label className="block">
              <span className="mb-1.5 block text-xs font-medium uppercase tracking-[0.12em] text-muted-foreground">
                Name
              </span>
              <input
                type="text"
                placeholder="Your name"
                value={form.name}
                onChange={(event) => setForm({ ...form, name: event.target.value })}
                className="h-11 w-full rounded-xl border border-white/70 bg-white/60 px-3 text-sm text-foreground shadow-sm outline-none transition focus:border-forest/50 focus:bg-white/80 focus:ring-4 focus:ring-forest/10"
              />
            </label>

            <label className="block">
              <span className="mb-1.5 block text-xs font-medium uppercase tracking-[0.12em] text-muted-foreground">
                Email
              </span>
              <input
                type="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={(event) => setForm({ ...form, email: event.target.value })}
                className="h-11 w-full rounded-xl border border-white/70 bg-white/60 px-3 text-sm text-foreground shadow-sm outline-none transition focus:border-forest/50 focus:bg-white/80 focus:ring-4 focus:ring-forest/10"
              />
            </label>

            <button
              type="submit"
              className="mt-2 h-11 w-full rounded-xl bg-forest text-sm font-medium text-white shadow-lg shadow-forest/20 transition hover:bg-deep"
            >
              Continue
            </button>
            {error && <p className="text-xs text-risk-high">{error}</p>}
          </form>
        </div>
      </div>
    </div>
  );
}
