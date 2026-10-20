import React, { useState, useEffect, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { QuickCommandModal } from './components/QuickCommandModal';
import { api } from './api';
import { SystemSnapshotResponse } from './types';

// Group A: System Pages
import { DashboardPage } from './pages/DashboardPage';
import { LiveMonitorPage } from './pages/LiveMonitorPage';
import { ProcessManagerPage } from './pages/ProcessManagerPage';
import { AutomationPage } from './pages/AutomationPage';
import { AlertsAndAnalyticsPage } from './pages/AlertsAndAnalyticsPage';

// Group B: OS Labs Pages (Units 1 to 6)
import { Unit1OverviewPage } from './pages/Unit1OverviewPage';
import { Unit2CpuSchedulingPage } from './pages/Unit2CpuSchedulingPage';
import { Unit3SyncDeadlocksPage } from './pages/Unit3SyncDeadlocksPage';
import { Unit4MemoryManagementPage } from './pages/Unit4MemoryManagementPage';
import { Unit5FilesystemPage } from './pages/Unit5FilesystemPage';
import { Unit6KernelAndroidPage } from './pages/Unit6KernelAndroidPage';

export const App: React.FC = () => {
  const [currentRoute, setCurrentRoute] = useState<string>('dashboard');
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [quickCommandOpen, setQuickCommandOpen] = useState<boolean>(false);
  const [snapshot, setSnapshot] = useState<SystemSnapshotResponse | null>(null);
  const [loadingSnapshot, setLoadingSnapshot] = useState<boolean>(false);

  // Fetch telemetry snapshot
  const fetchSnapshot = useCallback(async () => {
    try {
      setLoadingSnapshot(true);
      const data = await api.getSnapshot();
      setSnapshot(data);
    } catch (err) {
      console.error('Failed to fetch snapshot:', err);
    } finally {
      setLoadingSnapshot(false);
    }
  }, []);

  // Periodic snapshot polling
  useEffect(() => {
    fetchSnapshot();
    const interval = setInterval(fetchSnapshot, 3000);
    return () => clearInterval(interval);
  }, [fetchSnapshot]);

  // Global keyboard shortcut: Ctrl+K / Cmd+K to open Quick Command Modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setQuickCommandOpen((prev) => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Simplified Route Handler (11 routes)
  const renderCurrentPage = () => {
    switch (currentRoute) {
      // Group A: SYSTEM
      case 'dashboard':
        return <DashboardPage snapshot={snapshot} onNavigate={(tab) => setCurrentRoute(tab)} />;
      case 'monitor':
        return <LiveMonitorPage snapshot={snapshot} />;
      case 'processes':
        return <ProcessManagerPage />;
      case 'automation':
        return <AutomationPage />;
      case 'analytics':
        return <AlertsAndAnalyticsPage />;

      // Group B: OS LABS
      case 'unit1':
        return <Unit1OverviewPage />;
      case 'unit2':
        return <Unit2CpuSchedulingPage />;
      case 'unit3':
        return <Unit3SyncDeadlocksPage />;
      case 'unit4':
        return <Unit4MemoryManagementPage />;
      case 'unit5':
        return <Unit5FilesystemPage />;
      case 'unit6':
        return <Unit6KernelAndroidPage />;

      default:
        return <DashboardPage snapshot={snapshot} onNavigate={(tab) => setCurrentRoute(tab)} />;
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#070a13] text-slate-100 font-sans">
      {/* 2-Group Collapsible Sidebar */}
      <Sidebar
        currentRoute={currentRoute}
        onRouteChange={setCurrentRoute}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed((prev) => !prev)}
      />

      {/* Main Workspace */}
      <div className="flex flex-col flex-1 h-full min-w-0 overflow-hidden">
        {/* Top Navbar */}
        <Navbar
          currentRoute={currentRoute}
          snapshot={snapshot}
          loading={loadingSnapshot}
          onRefresh={fetchSnapshot}
          onOpenQuickCommand={() => setQuickCommandOpen(true)}
        />

        {/* Scrollable View Area */}
        <main className="flex-1 overflow-y-auto px-6 py-6 scroll-smooth bg-gradient-to-b from-[#090d19] to-[#070a13]">
          <div className="max-w-7xl mx-auto pb-12">
            {renderCurrentPage()}
          </div>
        </main>
      </div>

      {/* Quick Linux Command Modal (Ctrl+K) */}
      <QuickCommandModal
        isOpen={quickCommandOpen}
        onClose={() => setQuickCommandOpen(false)}
      />
    </div>
  );
};

export default App;
