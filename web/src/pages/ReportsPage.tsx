import React, { useState } from 'react'
import {
  FileText,
  Download,
  FileSpreadsheet,
  CheckCircle,
  Loader2,
  FileCode,
  Layers,
} from 'lucide-react'
import { api } from '../api'

export const ReportsPage: React.FC = () => {
  const [downloading, setDownloading] = useState<string | null>(null)
  const [statusMsg, setStatusMsg] = useState<string | null>(null)

  const handleDownload = async (type: string) => {
    setDownloading(type)
    setStatusMsg(null)
    try {
      // Trigger browser download via native link
      const link = document.createElement('a')
      link.href = `/api/reports/download/${type}`
      link.target = '_blank'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      setStatusMsg(`Successfully initiated export for ${type}.`)
    } catch (err: any) {
      alert(`Export failed: ${err.message}`)
    } finally {
      setDownloading(null)
    }
  }

  const reportsList = [
    {
      id: 'pdf',
      title: 'Full Platform PDF Report',
      description: 'Comprehensive multi-page publication-quality system report generated with ReportLab.',
      format: 'PDF',
      icon: FileText,
      color: 'text-rose-400 bg-rose-500/10 border-rose-500/30',
    },
    {
      id: 'txt',
      title: 'System Performance Plain Text Report',
      description: 'Human-readable detailed summary with historical metrics, top processes, and forecast curves.',
      format: 'TXT',
      icon: FileCode,
      color: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30',
    },
    {
      id: 'csv_metrics',
      title: 'Resource Telemetry Time Series',
      description: 'Granular CSV export of CPU, memory, swap, disk, network, and load average data points.',
      format: 'CSV',
      icon: FileSpreadsheet,
      color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30',
    },
    {
      id: 'csv_tasks',
      title: 'Automation Execution Log',
      description: 'CSV export of all executed tasks, commands, exit codes, and execution durations.',
      format: 'CSV',
      icon: FileSpreadsheet,
      color: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/30',
    },
    {
      id: 'csv_alerts',
      title: 'Incident & Alert Log',
      description: 'CSV export of all generated warning and critical threshold incidents.',
      format: 'CSV',
      icon: FileSpreadsheet,
      color: 'text-amber-400 bg-amber-500/10 border-amber-500/30',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
        <h2 className="text-lg font-bold text-white flex items-center gap-2">
          <FileText size={18} className="text-cyan-400" />
          <span>System Audit Reports & Data Export Center</span>
        </h2>
        <p className="text-xs text-slate-400">
          Generate and export real system administration reports in TXT, CSV, and PDF formats using ReportLab.
        </p>
      </div>

      {statusMsg && (
        <div className="p-3.5 rounded-xl bg-emerald-950/40 border border-emerald-800 text-emerald-300 text-xs flex items-center gap-2">
          <CheckCircle size={15} />
          <span>{statusMsg}</span>
        </div>
      )}

      {/* Report Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {reportsList.map((r) => {
          const Icon = r.icon
          const isBusy = downloading === r.id
          return (
            <div
              key={r.id}
              className="p-5 rounded-2xl bg-slate-900 border border-slate-800 flex flex-col justify-between gap-4 hover:border-slate-700 transition"
            >
              <div className="flex items-start gap-4">
                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center border flex-shrink-0 ${r.color}`}
                >
                  <Icon size={24} />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-sm font-bold text-white">{r.title}</h3>
                    <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-300">
                      {r.format}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{r.description}</p>
                </div>
              </div>

              <button
                onClick={() => handleDownload(r.id)}
                disabled={isBusy}
                className="w-full py-2.5 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-800 text-cyan-400 hover:text-cyan-300 text-xs font-semibold flex items-center justify-center gap-2 transition"
              >
                {isBusy ? <Loader2 size={15} className="animate-spin" /> : <Download size={15} />}
                <span>Generate & Download {r.format}</span>
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}
