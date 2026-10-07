import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';
import type { HealthEcosystemResponse, EngineStatus } from '../types';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { CheckCircle, XCircle, AlertCircle, Clock, Server, Database } from 'lucide-react';

interface StatusBadgeProps {
  status: EngineStatus;
}

function StatusBadge({ status }: StatusBadgeProps) {
  const config = {
    AVAILABLE: { color: 'bg-green-100 text-green-800', icon: CheckCircle, label: 'Available' },
    NOT_INSTALLED: { color: 'bg-red-100 text-red-800', icon: XCircle, label: 'Not Installed' },
    NOT_CONFIGURED: { color: 'bg-yellow-100 text-yellow-800', icon: AlertCircle, label: 'Not Configured' },
    CONFIGURED_BUT_OFFLINE: { color: 'bg-orange-100 text-orange-800', icon: Clock, label: 'Offline' },
    EXECUTION_FAILED: { color: 'bg-red-100 text-red-800', icon: XCircle, label: 'Execution Failed' },
    VALIDATED_LOCALLY: { color: 'bg-blue-100 text-blue-800', icon: CheckCircle, label: 'Validated Locally' },
  };

  const { color, icon: Icon, label } = config[status];

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${color}`}>
      <Icon className="w-3 h-3" />
      {label}
    </span>
  );
}

export function Ecosystem() {
  const [health, setHealth] = useState<HealthEcosystemResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadHealth();
  }, []);

  const loadHealth = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await apiClient.getHealthEcosystem();
      setHealth(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load ecosystem health');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingState message="Loading ecosystem status..." />;
  if (error) return <ErrorState message={error} onRetry={loadHealth} />;
  if (!health) return <ErrorState message="No ecosystem data available" />;

  const coreEngines = health.engines.filter(e => 
    ['PYTHON_BASELINE', 'MAPREDUCE', 'PYSPARK', 'SPARK_SQL'].includes(e.engine_type)
  );

  const optionalEngines = health.engines.filter(e => 
    ['HADOOP', 'HIVE', 'PIG', 'SQOOP'].includes(e.engine_type)
  );

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">BDA Ecosystem & Pipeline Monitor</h1>
        <p className="text-slate-600 mt-1">What the demo actually runs, and what is optional</p>
      </div>

      <div className="border-l-4 border-blue-700 bg-blue-50 px-5 py-4"><p className="text-sm font-semibold text-blue-950">Active BDA processing path</p><p className="mt-1 text-sm leading-6 text-slate-700">The 100,000-record JSONL dataset is analyzed with Python/pandas and a local MapReduce-style pipeline. The Reconciliation page also runs real PySpark DataFrame and Spark SQL aggregations in local mode and compares their results. Hadoop, Sqoop, Hive, and Pig remain optional extensions; the local MapReduce demonstration is not a distributed Hadoop cluster.</p></div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className={`bg-white border rounded-lg p-6 shadow-sm ${
          health.system_status === 'operational' ? 'border-green-200' : 'border-red-200'
        }`}>
          <div className="flex items-center gap-3">
            <Server className={`w-8 h-8 ${
              health.system_status === 'operational' ? 'text-green-600' : 'text-red-600'
            }`} />
            <div>
              <h3 className="text-sm font-medium text-slate-600">System Status</h3>
              <p className={`text-lg font-bold ${
                health.system_status === 'operational' ? 'text-green-700' : 'text-red-700'
              }`}>
                {health.system_status.toUpperCase()}
              </p>
            </div>
          </div>
        </div>

        <div className={`bg-white border rounded-lg p-6 shadow-sm ${
          health.mongodb_connected ? 'border-green-200' : 'border-red-200'
        }`}>
          <div className="flex items-center gap-3">
            <Database className={`w-8 h-8 ${
              health.mongodb_connected ? 'text-green-600' : 'text-red-600'
            }`} />
            <div>
          <h3 className="text-sm font-medium text-slate-600">Optional MongoDB cache</h3>
              <p className={`text-lg font-bold ${
                health.mongodb_connected ? 'text-green-700' : 'text-red-700'
              }`}>
                {health.mongodb_connected ? 'Connected' : 'Offline · analytics still run'}
              </p>
            </div>
          </div>
        </div>

        <div className={`bg-white border rounded-lg p-6 shadow-sm ${
          health.dataset_loaded ? 'border-green-200' : 'border-red-200'
        }`}>
          <div className="flex items-center gap-3">
            <Server className={`w-8 h-8 ${
              health.dataset_loaded ? 'text-green-600' : 'text-red-600'
            }`} />
            <div>
              <h3 className="text-sm font-medium text-slate-600">Dataset</h3>
              <p className={`text-lg font-bold ${
                health.dataset_loaded ? 'text-green-700' : 'text-red-700'
              }`}>
                {health.dataset_loaded ? 'Loaded' : 'Not Found'}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
        <div className="p-6 border-b border-slate-200">
          <h3 className="text-lg font-semibold text-slate-900">Active local processing path</h3>
          <p className="text-sm text-slate-600 mt-1">Applied by the analytics and reconciliation workflows; Spark runs locally without a cluster</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Engine</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Description</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Version</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Last Checked</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {coreEngines.map((engine) => (
                <tr key={engine.engine_type} className="hover:bg-slate-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                    {engine.engine_type.replace('_', ' ')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <StatusBadge status={engine.status} />
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-600">{engine.description}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    {engine.version || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                    {new Date(engine.last_checked).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {optionalEngines.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-lg shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-200">
            <h3 className="text-lg font-semibold text-slate-900">Optional ecosystem extensions</h3>
            <p className="text-sm text-slate-600 mt-1">Readiness checks only. These tools are not invoked by the current analytics path.</p>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Engine</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Description</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Version</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-600 uppercase tracking-wider">Last Checked</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {optionalEngines.map((engine) => (
                  <tr key={engine.engine_type} className="hover:bg-slate-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                      {engine.engine_type.replace('_', ' ')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <StatusBadge status={engine.status} />
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-600">{engine.description}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {engine.version || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {new Date(engine.last_checked).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {health.last_pipeline_run && (
        <div className="bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-900 mb-2">Last Pipeline Run</h3>
          <p className="text-slate-600">{new Date(health.last_pipeline_run).toLocaleString()}</p>
        </div>
      )}
    </div>
  );
}
