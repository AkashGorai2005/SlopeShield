import { Link } from "@/lib/navigation";

export default function Logo({ compact = false, to = "/" }) {
  return (
    <Link to={to} className="flex items-center gap-2.5">
      <span className="grid h-9 w-9 place-items-center overflow-hidden rounded-xl bg-forest/95 ring-1 ring-forest/20 shadow-sm">
      <img
        src="/logo.png"
        alt="SlopeShield"
        className="h-full w-full object-contain scale-[1.8]"
      />
      </span>
      {!compact && (
        <span className="font-display text-[20px] font-semibold tracking-tight text-deep">
          SlopeShield
        </span>
      )}
    </Link>
  );
}
