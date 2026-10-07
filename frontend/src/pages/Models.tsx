import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import type { ModelAnalytics } from '../types';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export function Models() {
  const [models, setModels] = useState<ModelAnalytics[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getModelAnalytics();
      setModels(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load model analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingState message="Loading model analytics..." />;
  if (error) return <ErrorState message={error} onRetry={loadModels} />;
  if (!models.length) return <ErrorState message="No model data available" />;

  const barData = models.map(model => ({
    model: model.model,
    'Token Total': model.token_total,
    'Record Count': model.record_count,
    'Success Rate': model.success_rate,
    'Quality Score': model.quality_score_average * 100,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Model Intelligence</h1>
        <p className="text-slate-600 mt-1">Compare provider/model workload and outcomes</p>
      </div>

      <div className="border-l-4 border-emerald-700 bg-emerald-50 px-5 py-4"><p className="text-sm font-semibold text-emerald-950">Question this page answers</p><p className="mt-1 text-sm leading-6 text-slate-700">How does workload and observed outcome vary across the model labels in this dataset? Compare volume, token use, success rate, and average quality by model. These are descriptive comparisons, not a controlled benchmark of model capability.</p></div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
      <div className="border-t-4 border-emerald-700 bg-white p-6 shadow-sm">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-emerald-800">Workload · 01</p>
        <h3 className="mt-1 text-lg font-semibold text-slate-900">Token volume by model</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis type="number" stroke="#475569" />
            <YAxis dataKey="model" type="category" width={120} stroke="#475569" />
            <Tooltip />
            <Legend />
            <Bar dataKey="Token Total" fill="#2563EB" name="Total Tokens" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="border-t-4 border-slate-500 bg-white p-6 shadow-sm">
        <p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-600">Workload · 02</p>
        <h3 className="mt-1 text-lg font-semibold text-slate-900">Record volume by model</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={barData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis type="number" stroke="#475569" />
            <YAxis dataKey="model" type="category" width={120} stroke="#475569" />
            <Tooltip />
            <Legend />
            <Bar dataKey="Record Count" fill="#475569" name="Records" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      </div>

      <div className="border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex flex-wrap items-end justify-between gap-2">
          <div><p className="text-xs font-bold uppercase tracking-[0.16em] text-emerald-800">Outcome comparison · 03</p><h3 className="mt-1 text-lg font-semibold text-slate-900">Success and quality by model</h3></div>
          <p className="text-xs text-slate-500">Both measures use a 0–100% scale</p>
        </div>
        <ResponsiveContainer width="100%" height={340}>
          <BarChart data={barData} layout="vertical" margin={{ left: 16, right: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis type="number" domain={[0, 100]} unit="%" stroke="#475569" />
            <YAxis dataKey="model" type="category" width={130} stroke="#475569" />
            <Tooltip />
            <Legend />
            <Bar dataKey="Success Rate" fill="#10B981" name="Success Rate (%)" />
            <Bar dataKey="Quality Score" fill="#F59E0B" name="Quality Score (%)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Model Details</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Model</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Records</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Tokens</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Avg Tokens</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Success Rate</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Quality Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Categories</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {models.map((model) => (
                <tr key={model.model} className="hover:bg-slate-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{model.model}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{model.record_count.toLocaleString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{model.token_total.toLocaleString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{model.token_average.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{model.success_rate.toFixed(1)}%</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{model.quality_score_average.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{model.categories_processed.join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
