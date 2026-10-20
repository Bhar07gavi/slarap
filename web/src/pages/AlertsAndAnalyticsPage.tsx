import React, { useState } from 'react'
import {
  Bell,
  TrendingUp,
  Lightbulb,
  FileText,
} from 'lucide-react'
import { AlertsPage } from './AlertsPage'
import { PredictiveAnalyticsPage } from './PredictiveAnalyticsPage'
import { RecommendationsPage } from './RecommendationsPage'
import { ReportsPage } from './ReportsPage'

export const AlertsAndAnalyticsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'alerts' | 'predictions' | 'recommendations' | 'reports'>('alerts')

  return (
    <div className="space-y-6">
      {/* Sub-navigation Tabs */}
      <div className="flex flex-wrap items-center gap-2 p-1.5 bg-slate-900 border border-slate-800 rounded-xl">
        <button
          onClick={() => setActiveTab('alerts')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
            activeTab === 'alerts'
              ? 'bg-cyan-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <Bell size={15} />
          <span>System Alerts & Thresholds</span>
        </button>

        <button
          onClick={() => setActiveTab('predictions')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
            activeTab === 'predictions'
              ? 'bg-cyan-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <TrendingUp size={15} />
          <span>Predictive Trend Analytics</span>
        </button>

        <button
          onClick={() => setActiveTab('recommendations')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
            activeTab === 'recommendations'
              ? 'bg-cyan-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <Lightbulb size={15} />
          <span>Smart Recommendations</span>
        </button>

        <button
          onClick={() => setActiveTab('reports')}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
            activeTab === 'reports'
              ? 'bg-cyan-600 text-white shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
          }`}
        >
          <FileText size={15} />
          <span>Reports & Data Exports</span>
        </button>
      </div>

      {/* Tab Content */}
      <div className="transition-all duration-200">
        {activeTab === 'alerts' && <AlertsPage />}
        {activeTab === 'predictions' && <PredictiveAnalyticsPage />}
        {activeTab === 'recommendations' && <RecommendationsPage />}
        {activeTab === 'reports' && <ReportsPage />}
      </div>
    </div>
  )
}
