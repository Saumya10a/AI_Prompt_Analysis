import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import type { ReconciliationReport } from '../types';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { Check, X } from 'lucide-react';

export function Reconciliation() {
  const [reports, setReports] = useState<ReconciliationReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<'all' | 'mismatched' | 'matched'>('all');

  useEffect(() => {
    loadReconciliation();
  }, []);

  const loadReconciliation = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getReconciliationReports();
      setReports(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load reconciliation reports');
    } finally {
      setLoading(false);
    }
  };

  const filteredReports = reports.filter(report => {
    if (filterType === 'matched') return report.match_status;
    if (filterType === 'mismatched') return !report.match_status;
    return true;
  });

  const matchRate = reports.length > 0 
    ? (reports.filter(r => r.match_status).length / reports.length * 100).toFixed(1)
    : '0.0';

  if (loading) return <LoadingState message="Loading reconciliation reports..." />;
  if (error) return <ErrorState message={error} onRetry={loadReconciliation} />;
  if (!reports.length) return <ErrorState message="No reconciliation data available" />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Data Reconciliation</h1>
        <p className="text-slate-600 mt-1">Compare the same metrics across Python, local MapReduce, PySpark, and Spark SQL.</p>
      </div>

      <div className="border-l-4 border-violet-700 bg-violet-50 px-5 py-4"><p className="text-sm font-semibold text-violet-950">Why reconciliation matters</p><p className="mt-1 text-sm leading-6 text-slate-700">Each metric is recalculated through three paths—local MapReduce, PySpark DataFrames, and Spark SQL—and checked against the Python baseline. Matching results demonstrate that different big data processing approaches produce consistent analytics on the same 100,000-record dataset. Spark runs locally in this project; Hadoop cluster execution is an optional extension.</p></div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-sm font-medium text-slate-600 uppercase tracking-wide">Total Comparisons</h3>
          <p className="mt-2 text-3xl font-bold text-slate-900">{reports.length}</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-sm font-medium text-slate-600 uppercase tracking-wide">Match Rate</h3>
          <p className="mt-2 text-3xl font-bold text-green-600">{matchRate}%</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-sm font-medium text-slate-600 uppercase tracking-wide">Mismatches</h3>
          <p className="mt-2 text-3xl font-bold text-red-600">
            {reports.filter(r => !r.match_status).length}
          </p>
        </div>
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => setFilterType('all')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            filterType === 'all'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50'
          }`}
        >
          All
        </button>
        <button
          onClick={() => setFilterType('matched')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            filterType === 'matched'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50'
          }`}
        >
          Matched
        </button>
        <button
          onClick={() => setFilterType('mismatched')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            filterType === 'mismatched'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50'
          }`}
        >
          Mismatched
        </button>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Engine Comparison Results</h3>
          <p className="text-sm text-slate-600 mt-1">
            Showing {filteredReports.length} of {reports.length} comparisons
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                  Metric
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                  Engine A (per row)
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                  Engine B (per row)
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                  Absolute Delta
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                  Percentage Delta
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">
                  Timestamp
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {filteredReports.map((report, index) => (
                <tr key={index} className="hover:bg-slate-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    {report.match_status ? (
                      <div className="flex items-center gap-1 text-green-600">
                        <Check className="w-4 h-4" />
                        <span className="text-sm font-medium">Match</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-1 text-red-600">
                        <X className="w-4 h-4" />
                        <span className="text-sm font-medium">Mismatch</span>
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-900 font-medium">
                    {report.metric_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    <span className="block text-xs text-slate-400">{report.engine_a}</span>
                    {typeof report.value_a === 'number' ? report.value_a.toFixed(4) : report.value_a}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    <span className="block text-xs text-slate-400">{report.engine_b}</span>
                    {typeof report.value_b === 'number' ? report.value_b.toFixed(4) : report.value_b}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                    report.match_status ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {report.absolute_delta.toFixed(4)}
                  </td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                    report.match_status ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {report.percentage_delta !== null ? `${report.percentage_delta.toFixed(2)}%` : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    {new Date(report.timestamp).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredReports.length === 0 && (
        <div className="bg-white border border-slate-200 rounded-lg p-12 text-center">
          <p className="text-slate-600">No reports match the current filter</p>
        </div>
      )}
    </div>
  );
}
