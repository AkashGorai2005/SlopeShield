import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { riskColor, riskLabel } from "@/utils/riskUtils";

const axis = { stroke: "var(--color-muted-foreground)", fontSize: 11, tickLine: false, axisLine: false };
const grid = <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />;
const tooltipStyle = {
  contentStyle: {
    borderRadius: 8,
    border: "1px solid var(--color-border)",
    background: "var(--color-card)",
    fontSize: 12,
    boxShadow: "var(--shadow-panel)",
  },
};

export default function RiskChart({ type, data, title, subtitle, height = 260, className = "" }) {
  return (
    <section className={`panel p-5 ${className}`}>
      {title && (
        <header className="mb-4">
          <h3 className="text-base text-deep">{title}</h3>
          {subtitle && <p className="mt-0.5 text-xs text-muted-foreground">{subtitle}</p>}
        </header>
      )}
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          {renderChart(type, data)}
        </ResponsiveContainer>
      </div>
    </section>
  );
}

function renderChart(type, data) {
  switch (type) {
    case "rainfall-vs-risk":
      return (
        <AreaChart data={data} margin={{ left: -18, right: 6, top: 6 }}>
          <defs>
            <linearGradient id="rainFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--color-sage)" stopOpacity={0.5} />
              <stop offset="100%" stopColor="var(--color-sage)" stopOpacity={0.04} />
            </linearGradient>
          </defs>
          {grid}
          <XAxis dataKey="day" {...axis} />
          <YAxis {...axis} />
          <Tooltip {...tooltipStyle} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Area
            type="monotone"
            dataKey="rainfall"
            name="Rainfall (mm)"
            stroke="var(--color-sage)"
            fill="url(#rainFill)"
            strokeWidth={2}
          />
          <Line type="monotone" dataKey="risk" name="Risk index" stroke="var(--color-risk-high)" strokeWidth={2} dot={false} />
        </AreaChart>
      );

    case "risk-trend":
      return (
        <LineChart data={data} margin={{ left: -18, right: 6, top: 6 }}>
          {grid}
          <XAxis dataKey="day" {...axis} />
          <YAxis {...axis} allowDecimals={false} />
          <Tooltip {...tooltipStyle} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          {["low", "moderate", "high", "critical"].map((k) => (
            <Line
              key={k}
              type="monotone"
              dataKey={k}
              name={riskLabel(k)}
              stroke={riskColor(k)}
              strokeWidth={2}
              dot={false}
            />
          ))}
        </LineChart>
      );

    case "distribution":
      return (
        <PieChart>
          <Tooltip {...tooltipStyle} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Pie
            data={data.map((d) => ({ ...d, name: riskLabel(d.level) }))}
            dataKey="count"
            nameKey="name"
            innerRadius="55%"
            outerRadius="82%"
            paddingAngle={2}
          >
            {data.map((d) => (
              <Cell key={d.level} fill={riskColor(d.level)} stroke="var(--color-card)" strokeWidth={2} />
            ))}
          </Pie>
        </PieChart>
      );

    case "regional":
      return (
        <BarChart data={data} margin={{ left: -18, right: 6, top: 6 }}>
          {grid}
          <XAxis dataKey="region" {...axis} interval={0} angle={-20} textAnchor="end" height={54} />
          <YAxis {...axis} />
          <Tooltip {...tooltipStyle} />
          <Legend wrapperStyle={{ fontSize: 11 }} />
          <Bar dataKey="risk" name="Risk index" fill="var(--color-forest)" radius={[4, 4, 0, 0]} />
          <Bar dataKey="rainfall" name="Rainfall (mm)" fill="var(--color-sage)" radius={[4, 4, 0, 0]} />
        </BarChart>
      );

    case "factors":
      return (
        <BarChart data={data} layout="vertical" margin={{ left: 42, right: 12 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" horizontal={false} />
          <XAxis type="number" {...axis} unit="%" />
          <YAxis type="category" dataKey="factor" {...axis} width={110} />
          <Tooltip {...tooltipStyle} />
          <Bar dataKey="weight" name="Model importance" fill="var(--color-olive)" radius={[0, 4, 4, 0]} />
        </BarChart>
      );

    case "location-rainfall":
    default:
      return (
        <BarChart data={data} margin={{ left: -18, right: 6, top: 6 }}>
          {grid}
          <XAxis dataKey="day" {...axis} />
          <YAxis {...axis} />
          <Tooltip {...tooltipStyle} />
          <Bar dataKey="rainfall" name="Rainfall (mm)" fill="var(--color-sage)" radius={[4, 4, 0, 0]} />
        </BarChart>
      );
  }
}
