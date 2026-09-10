import React from 'react';
import { useSelector } from 'react-redux';
import {
  Sparkles,
  AlertOctagon,
  AlertTriangle,
  Info,
  HelpCircle,
  ArrowRightCircle,
  FileText,
} from 'lucide-react';

export default function RiskAssessmentPanel() {
  const { riskAssessment } = useSelector((state) => state.complaint);
  const severity = riskAssessment?.severity || 'Not Assessed';
  const nextAction = riskAssessment?.suggested_next_action || riskAssessment?.suggested_actions?.[0] || 'Awaiting Risk Evaluation';
  const initialRisk = riskAssessment?.initial_risk_assessment || riskAssessment?.risk_rationale || riskAssessment?.rationale || 'Awaiting complaint details to calculate automated ICH Q9 risk assessment.';

  const getSeverityBadge = () => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return {
          bg: 'bg-red-50 text-red-700 border-red-200 ring-1 ring-red-500/20',
          dot: 'bg-red-600 animate-pulse',
          icon: <AlertOctagon className="w-3.5 h-3.5 text-red-600" />,
          label: 'Critical',
        };
      case 'major':
        return {
          bg: 'bg-amber-50 text-amber-800 border-amber-200 ring-1 ring-amber-500/20',
          dot: 'bg-amber-500',
          icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />,
          label: 'Major',
        };
      case 'minor':
        return {
          bg: 'bg-blue-50 text-blue-700 border-blue-200 ring-1 ring-blue-500/20',
          dot: 'bg-blue-500',
          icon: <Info className="w-3.5 h-3.5 text-blue-600" />,
          label: 'Minor',
        };
      default:
        return {
          bg: 'bg-slate-100 text-slate-600 border-slate-200',
          dot: 'bg-slate-400',
          icon: <HelpCircle className="w-3.5 h-3.5 text-slate-500" />,
          label: 'Not Assessed',
        };
    }
  };

  const badge = getSeverityBadge();

  return (
    <div className="bg-purple-50/40 border border-purple-200/80 rounded-xl p-4 space-y-3.5 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-purple-600" />
          <h3 className="font-bold text-xs uppercase tracking-wider text-purple-900">
            AI Copilot Risk Assessment
          </h3>
        </div>
      </div>

      {/* Two-Column Row: Severity (Suggested) & Suggested Next Action */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
        <div className="bg-white/80 p-3 rounded-lg border border-purple-100 space-y-1">
          <span className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Severity (Suggested)
          </span>
          <div className="pt-0.5">
            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full font-bold text-xs border ${badge.bg}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${badge.dot}`} />
              {badge.icon}
              <span>{badge.label}</span>
            </span>
          </div>
        </div>

        <div className="bg-white/80 p-3 rounded-lg border border-purple-100 space-y-1">
          <span className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Suggested Next Action
          </span>
          <div className="flex items-center gap-1.5 font-medium text-slate-800 pt-0.5">
            <ArrowRightCircle className="w-3.5 h-3.5 text-purple-600 shrink-0" />
            <span className="truncate">{nextAction}</span>
          </div>
        </div>
      </div>

      {/* Full-width Block: Initial Risk Assessment */}
      <div className="bg-white/90 p-3 rounded-lg border border-purple-100 space-y-1 text-xs">
        <span className="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1.5">
          <FileText className="w-3 h-3 text-purple-600" />
          Initial Risk Assessment
        </span>
        <p className="text-slate-700 leading-relaxed text-xs">
          {initialRisk}
        </p>
      </div>
    </div>
  );
}

