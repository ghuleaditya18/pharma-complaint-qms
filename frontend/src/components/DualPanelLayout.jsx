import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Shield, RotateCcw, AlertCircle } from 'lucide-react';
import ComplaintForm from './ComplaintForm.jsx';
import ChatCopilot from './ChatCopilot.jsx';
import { resetComplaintState } from '../features/complaintSlice.js';

export default function DualPanelLayout() {
  const dispatch = useDispatch();
  const { error } = useSelector((state) => state.complaint);

  const handleReset = () => {
    if (window.confirm('Start a new complaint? Current unsaved form data will be reset.')) {
      dispatch(resetComplaintState());
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col font-sans">
      {/* Top Application Navbar */}
      <header className="bg-white border-b border-slate-200/90 sticky top-0 z-30 shadow-2xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Brand Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 to-indigo-800 flex items-center justify-center text-white shadow-sm shadow-indigo-200">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold text-slate-900 tracking-tight leading-none">
                  AIVOA Pharma QMS
                </h1>
                <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 text-[10px] font-bold rounded-full uppercase tracking-wider border border-indigo-100">
                  GMP Copilot
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                ICH Q9 Complaint Intake, Auto-Extraction & Severity Classification
              </p>
            </div>
          </div>

          {/* Action Tools */}
          <div className="flex items-center gap-3">
            <button
              onClick={handleReset}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 active:bg-slate-100 text-slate-700 text-xs font-semibold transition-colors shadow-2xs"
            >
              <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
              <span>New Complaint</span>
            </button>
          </div>
        </div>
      </header>

      {/* Global Error Alert Banner (if any) */}
      {error && (
        <div className="bg-red-50 border-b border-red-200 px-4 py-2.5 text-xs text-red-700 flex items-center justify-between">
          <div className="max-w-7xl mx-auto flex items-center gap-2 w-full">
            <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* Main Dual Panel Body (50/50 desktop split) */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-8rem)] min-h-[720px]">
          {/* Left Panel: Auto-Populated Read-Only Complaint Form & Risk Assessment */}
          <section className="h-full overflow-hidden flex flex-col">
            <ComplaintForm />
          </section>

          {/* Right Panel: Conversational AI Copilot */}
          <section className="h-full overflow-hidden flex flex-col">
            <ChatCopilot />
          </section>
        </div>
      </main>
    </div>
  );
}
