import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import type { CategoryAnalytics } from '../types';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, PieChart, Pie, Cell } from 'recharts';

const CATEGORY_COLORS = ['#1D4ED8', '#0F766E', '#B45309', '#7C3AED', '#BE123C', '#475569', '#0891B2'];

export function Categories() {
  const [categories, setCategories] = useState<CategoryAnalytics[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getCategoryAnalytics();
      setCategories(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load category analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingState message="Loading category analytics..." />;
  if (error) return <ErrorState message={error} onRetry={loadCategories} />;
  if (!categories.length) return <ErrorState message="No category data available" />;

  const barData = categories.map(cat => ({
    category: cat.category,
    'Token Total': cat.token_total,
    'Record Count': cat.record_count,
    'Success Rate': cat.success_rate,
    'Quality Score': cat.quality_score_average * 100,
  }));
  const categoryChartHeight = Math.max(320, categories.length * 48);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Category Intelligence</h1>
        <p className="text-slate-600 mt-1">Workload distribution by task domain</p>
      </div>

      <div className="border-l-4 border-blue-700 bg-blue-50 px-5 py-4"><p className="text-sm font-semibold text-blue-950">Question this page answers</p><p className="mt-1 text-sm leading-6 text-slate-700">Which task categories account for the records and token use, and how do their outcomes compare? Category is the workload dimension here; use this view to discuss how analytics aggregates data by a business or task domain.</p></div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.4fr_0.8fr]">
        <div className="border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-blue-800">Composition view</p>
          <h3 className="mt-1 text-lg font-semibold text-slate-900">Share of total token workload</h3>
          <p className="mt-1 text-sm text-slate-600">Each segment represents a category’s share of all tokens.</p>
          <ResponsiveContainer width="100%" height={310}>
            <PieChart>
              <Pie data={barData} dataKey="Token Total" nameKey="category" cx="50%" cy="50%" innerRadius={70} outerRadius={112} paddingAngle={3}>
                {barData.map((entry, index) => <Cell key={entry.category} fill={CATEGORY_COLORS[index % CATEGORY_COLORS.length]} />)}
              </Pie>
              <Tooltip formatter={(value: number) => [`${value.toLocaleString()} tokens`, 'Total']} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="flex flex-col justify-center border border-blue-200 bg-blue-950 p-6 text-white">
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-blue-200">Read the distribution</p>
          <h3 className="mt-3 text-2xl font-semibold">Tokens show workload share</h3>
          <p className="mt-3 text-sm leading-6 text-blue-100">A larger segment means more of the dataset’s total token use comes from that task domain. Compare this with the record counts below to see whether volume or longer records explain the share.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
      <div className="border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Record Count by Category</h3>
        <ResponsiveContainer width="100%" height={categoryChartHeight}>
          <BarChart data={barData} layout="vertical" margin={{ left: 16, right: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis type="number" stroke="#475569" />
            <YAxis dataKey="category" type="category" width={185} tick={{ fontSize: 11 }} stroke="#475569" />
            <Tooltip />
            <Legend />
            <Bar dataKey="Record Count" fill="#475569" name="Records" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-lg font-semibold text-slate-900 mb-4">Success Rate & Quality Score by Category</h3>
        <ResponsiveContainer width="100%" height={categoryChartHeight}>
          <BarChart data={barData} layout="vertical" margin={{ left: 16, right: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis type="number" domain={[0, 100]} unit="%" stroke="#475569" />
            <YAxis dataKey="category" type="category" width={185} tick={{ fontSize: 11 }} stroke="#475569" />
            <Tooltip />
            <Legend />
            <Bar dataKey="Success Rate" fill="#10B981" name="Success Rate (%)" />
            <Bar dataKey="Quality Score" fill="#F59E0B" name="Quality Score (%)" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Category Details</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Category</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Records</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Tokens</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Avg Tokens</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Success Rate</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Quality Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Models Used</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {categories.map((cat) => (
                <tr key={cat.category} className="hover:bg-slate-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">{cat.category}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{cat.record_count.toLocaleString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{cat.token_total.toLocaleString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{cat.token_average.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{cat.success_rate.toFixed(1)}%</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{cat.quality_score_average.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">{cat.models_used.join(', ')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
