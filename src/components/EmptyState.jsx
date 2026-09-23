import { Leaf } from "lucide-react";

export default function EmptyState({ title = "Nothing to show", description, action, icon: Icon = Leaf }) {
  return (
    <div className="panel flex flex-col items-center justify-center px-6 py-12 text-center">
      <span className="grid h-11 w-11 place-items-center rounded-full bg-sage-soft text-forest">
        <Icon className="h-5 w-5" />
      </span>
      <p className="mt-3 text-sm font-medium text-foreground">{title}</p>
      {description && <p className="mt-1 max-w-sm text-sm text-muted-foreground">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
