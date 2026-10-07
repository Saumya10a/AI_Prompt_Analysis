interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'neutral';
}

export function KPICard({ title, value, subtitle }: KPICardProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
      <h3 className="text-sm font-medium text-slate-600 uppercase tracking-wide">{title}</h3>
      <p className="mt-2 text-3xl font-bold text-slate-900">{value}</p>
      {subtitle && (
        <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
      )}
    </div>
  );
}
