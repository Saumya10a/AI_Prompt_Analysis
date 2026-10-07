import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import type { OverviewStats } from '../types';
import { KPICard } from '../components/KPICard';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#2563EB', '#475569', '#64748B', '#94A3B8', '#CBD5E1'];

export function Overview() {
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadOverview();
  }, []);

  const loadOverview = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getOverviewAnalytics();
      setStats(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load overview data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingState message="Loading overview analytics..." />;
  if (error) return <ErrorState message={error} onRetry={loadOverview} />;
  if (!stats) return <ErrorState message="No overview data available" />;

  const kpiData = [
    { title: 'Total Records', value: stats.total_records.toLocaleString() },
    { title: 'Total Tokens', value: stats.total_tokens.toLocaleString() },
    { title: 'Avg Tokens/Record', value: stats.average_tokens_per_record.toFixed(2) },
    { title: 'Unique Categories', value: stats.unique_categories },
    { title: 'Unique Models', value: stats.unique_models },
    { title: 'Success Rate', value: `${stats.overall_success_rate.toFixed(1)}%` },
    { title: 'Quality Score', value: stats.overall_quality_score.toFixed(2) },
  ];

  const pieData = [
    { name: 'Categories', value: stats.unique_categories },
    { name: 'Models', value: stats.unique_models },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Executive Overview</h1>
        <p className="text-slate-600 mt-1">Key dataset metrics and performance indicators</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiData.map((kpi, index) => (
          <KPICard key={index} {...kpi} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Dataset Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((_, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">Performance Metrics</h3>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-600">Success Rate</span>
                <span className="font-medium text-slate-900">{stats.overall_success_rate.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${stats.overall_success_rate}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-600">Quality Score</span>
                <span className="font-medium text-slate-900">{stats.overall_quality_score.toFixed(2)}</span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full"
                  style={{ width: `${stats.overall_quality_score * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900 mb-2">Last Updated</h3>
        <p className="text-slate-600">{new Date(stats.generated_at).toLocaleString()}</p>
      </div>
    </div>
  );
}
