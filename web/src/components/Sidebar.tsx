import React from 'react'
import {
  LayoutDashboard,
  Activity,
  Cpu,
  Workflow,
  LineChart,
  BookOpen,
  Layers,
  ShieldCheck,
  HardDrive,
  FolderTree,
  Smartphone,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'

interface SidebarProps {
  currentRoute: string
  onRouteChange: (route: string) => void
  collapsed: boolean
  onToggleCollapse: () => void
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentRoute,
  onRouteChange,
  collapsed,
  onToggleCollapse,
}) => {
  const systemItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'monitor', label: 'Live Monitoring', icon: Activity },
    { id: 'processes', label: 'Process Manager', icon: Cpu },
    { id: 'automation', label: 'Automation', icon: Workflow },
    { id: 'analytics', label: 'Alerts & Analytics', icon: LineChart },
  ]

  const osLabItems = [
    { id: 'unit1', label: 'OS Overview', icon: BookOpen },
    { id: 'unit2', label: 'Process & CPU Scheduling', icon: Layers },
    { id: 'unit3', label: 'Synchronization & Deadlocks', icon: ShieldCheck },
    { id: 'unit4', label: 'Memory Management', icon: HardDrive },
    { id: 'unit5', label: 'File & I/O Management', icon: FolderTree },
    { id: 'unit6', label: 'Linux Kernel & Android OS', icon: Smartphone },
  ]

  return (
    <aside
      className={`relative flex flex-col bg-[#0b0f19] border-r border-slate-800 transition-all duration-300 z-30 select-none ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand Header */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-slate-800">
        <div
          className="flex items-center gap-3 cursor-pointer overflow-hidden"
          onClick={() => onRouteChange('dashboard')}
        >
          <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 text-white font-bold text-lg shadow-sm flex-shrink-0">
            S
          </div>
          {!collapsed && (
            <div className="flex flex-col">
              <span className="font-bold text-base tracking-wider text-slate-100 flex items-center gap-1.5">
                SLARAP
                <span className="text-[10px] uppercase font-semibold px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                  v2.0
                </span>
              </span>
              <span className="text-[11px] text-slate-400 truncate">Linux Admin & OS Labs</span>
            </div>
          )}
        </div>
        <button
          onClick={onToggleCollapse}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight size={17} /> : <ChevronLeft size={17} />}
        </button>
      </div>

      {/* Navigation Groups */}
      <div className="flex-1 overflow-y-auto px-3 py-5 space-y-6">
        {/* GROUP A: SYSTEM */}
        <div>
          {!collapsed && (
            <div className="px-3 mb-2 text-[11px] font-bold uppercase tracking-wider text-slate-400">
              System
            </div>
          )}
          <nav className="space-y-1">
            {systemItems.map((item) => {
              const Icon = item.icon
              const active = currentRoute === item.id
              return (
                <button
                  key={item.id}
                  onClick={() => onRouteChange(item.id)}
                  title={collapsed ? item.label : undefined}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition ${
                    active
                      ? 'bg-cyan-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon size={16} className={active ? 'text-white' : 'text-slate-400'} />
                  {!collapsed && <span className="truncate">{item.label}</span>}
                </button>
              )
            })}
          </nav>
        </div>

        {/* GROUP B: OS LABS */}
        <div>
          {!collapsed && (
            <div className="px-3 mb-2 text-[11px] font-bold uppercase tracking-wider text-indigo-400 flex items-center justify-between">
              <span>OS Labs</span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-indigo-950/80 text-indigo-300 border border-indigo-800">
                Units 1–6
              </span>
            </div>
          )}
          <nav className="space-y-1">
            {osLabItems.map((item) => {
              const Icon = item.icon
              const active = currentRoute === item.id
              return (
                <button
                  key={item.id}
                  onClick={() => onRouteChange(item.id)}
                  title={collapsed ? item.label : undefined}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition ${
                    active
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon size={16} className={active ? 'text-white' : 'text-slate-400'} />
                  {!collapsed && <span className="truncate">{item.label}</span>}
                </button>
              )
            })}
          </nav>
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-3 border-t border-slate-800 bg-[#070a13]/80">
        {!collapsed && (
          <div className="px-2 py-1.5 text-center text-[10px] text-slate-500 font-mono">
            OS Academic Edition
          </div>
        )}
      </div>
    </aside>
  )
}
