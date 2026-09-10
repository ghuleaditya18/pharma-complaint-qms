import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  FileText,
  Lock,
  Send,
  CheckCircle,
  Building,
  Package,
  Calendar,
  Layers,
  AlertCircle,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';
import { saveComplaint } from '../features/complaintSlice.js';
import RiskAssessmentPanel from './RiskAssessmentPanel.jsx';

export default function ComplaintForm() {
  const dispatch = useDispatch();
  const { formData, loading, savedComplaint } = useSelector(
    (state) => state.complaint
  );

  const handleSubmitToQMS = () => {
    dispatch(saveComplaint());
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-xl border border-slate-200/90 shadow-sm overflow-hidden">
      {/* Top Header */}
      <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold tracking-tight">Log Customer Complaint</h2>
          <p className="text-xs text-slate-400 font-medium mt-0.5">
            API & FDF Quality Assurance Module
          </p>
        </div>
        <div className="flex items-center gap-2">
          {savedComplaint ? (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full text-xs font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Committed to QMS
            </span>
          ) : (
            <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-purple-500/20 text-purple-300 border border-purple-500/30 rounded-full text-xs font-semibold">
              <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
              Ready to Commit
            </span>
          )}
        </div>
      </div>

      {/* Scrollable Form Body with 4 Numbered Sections */}
      <div className="p-6 overflow-y-auto space-y-6 flex-1 text-xs">
        {/* Section 1: Origin & Customer Details */}
        <div className="border border-slate-200 rounded-xl p-4 space-y-3.5 bg-slate-50/40">
          <div className="flex items-center gap-2 border-b border-slate-200/80 pb-2">
            <Building className="w-4 h-4 text-purple-600" />
            <h3 className="font-bold text-xs uppercase tracking-wider text-slate-800">
              1. ORIGIN & CUSTOMER DETAILS
            </h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block font-semibold text-slate-700 mb-1 flex items-center justify-between">
                <span>Complaint Source</span>
                <Lock className="w-3 h-3 text-slate-400" />
              </label>
              <input
                type="text"
                readOnly
                disabled
                value={formData.complaint_source || ''}
                placeholder="e.g., Pharmacy, Hospital, Distributor"
                className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-800 cursor-not-allowed text-xs focus:outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1 flex items-center justify-between">
                <span>Customer Name</span>
                <Lock className="w-3 h-3 text-slate-400" />
              </label>
              <input
                type="text"
                readOnly
                disabled
                value={formData.customer_name || ''}
                placeholder="e.g., Apollo Pharmacy, Dr. Sharma"
                className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-800 cursor-not-allowed text-xs focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Section 2: Product & Batch Identification */}
        <div className="border border-slate-200 rounded-xl p-4 space-y-3.5 bg-slate-50/40">
          <div className="flex items-center gap-2 border-b border-slate-200/80 pb-2">
            <Package className="w-4 h-4 text-purple-600" />
            <h3 className="font-bold text-xs uppercase tracking-wider text-slate-800">
              2. PRODUCT & BATCH IDENTIFICATION
            </h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block font-semibold text-slate-700 mb-1 flex items-center justify-between">
                <span>Product Name</span>
                <Lock className="w-3 h-3 text-slate-400" />
              </label>
              <input
                type="text"
                readOnly
                disabled
                value={formData.product_name || ''}
                placeholder="e.g., Amoxicillin Capsules"
                className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-800 cursor-not-allowed text-xs focus:outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1 flex items-center justify-between">
                <span>Product Strength</span>
                <Lock className="w-3 h-3 text-slate-400" />
              </label>
              <input
                type="text"
                readOnly
                disabled
                value={formData.product_strength || ''}
                placeholder="e.g., 500 mg, API Grade"
                className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-800 cursor-not-allowed text-xs focus:outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1 flex items-center justify-between">
                <span>Batch / Lot Number</span>
                <Lock className="w-3 h-3 text-slate-400" />
              </label>
              <input
                type="text"
                readOnly
                disabled
                value={formData.batch_number || ''}
                placeholder="e.g., BMX24602"
                className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-800 cursor-not-allowed text-xs font-mono focus:outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1 flex items-center justify-between">
                <span>Affected Quantity</span>
                <Lock className="w-3 h-3 text-slate-400" />
              </label>
              <input
                type="text"
                readOnly
                disabled
                value={formData.affected_quantity || ''}
                placeholder="e.g., 12 capsules, 50 kg"
                className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-800 cursor-not-allowed text-xs focus:outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1 flex items-center justify-between">
                <span>Manufacturing Date</span>
                <Lock className="w-3 h-3 text-slate-400" />
              </label>
              <input
                type="text"
                readOnly
                disabled
                value={formData.manufacturing_date || ''}
                placeholder="e.g., March 2026 or YYYY-MM-DD"
                className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-800 cursor-not-allowed text-xs focus:outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1 flex items-center justify-between">
                <span>Expiry Date</span>
                <Lock className="w-3 h-3 text-slate-400" />
              </label>
              <input
                type="text"
                readOnly
                disabled
                value={formData.expiry_date || ''}
                placeholder="e.g., February 2028 or YYYY-MM-DD"
                className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-800 cursor-not-allowed text-xs focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Section 3: Facility & Material Impact */}
        <div className="border border-slate-200 rounded-xl p-4 space-y-3.5 bg-slate-50/40">
          <div className="flex items-center gap-2 border-b border-slate-200/80 pb-2">
            <Layers className="w-4 h-4 text-purple-600" />
            <h3 className="font-bold text-xs uppercase tracking-wider text-slate-800">
              3. FACILITY & MATERIAL IMPACT
            </h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block font-semibold text-slate-700 mb-1 flex items-center justify-between">
                <span>Originating Site Block</span>
                <Lock className="w-3 h-3 text-slate-400" />
              </label>
              <input
                type="text"
                readOnly
                disabled
                value={formData.originating_site_block || ''}
                placeholder="e.g., Manufacturing, Packaging, Warehouse"
                className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-800 cursor-not-allowed text-xs focus:outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1 flex items-center justify-between">
                <span>Impacted Non-Product Materials (NPM)</span>
                <Lock className="w-3 h-3 text-slate-400" />
              </label>
              <input
                type="text"
                readOnly
                disabled
                value={formData.impacted_npm || ''}
                placeholder="e.g., Primary Packaging (Bottle), Blister Foil"
                className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-800 cursor-not-allowed text-xs focus:outline-none"
              />
            </div>
          </div>
        </div>

        {/* Section 4: Defect Analysis */}
        <div className="border border-slate-200 rounded-xl p-4 space-y-3.5 bg-slate-50/40">
          <div className="flex items-center gap-2 border-b border-slate-200/80 pb-2">
            <FileText className="w-4 h-4 text-purple-600" />
            <h3 className="font-bold text-xs uppercase tracking-wider text-slate-800">
              4. DEFECT ANALYSIS
            </h3>
          </div>
          <div className="space-y-3.5">
            <div>
              <label className="block font-semibold text-slate-700 mb-1 flex items-center justify-between">
                <span>Complaint Category</span>
                <Lock className="w-3 h-3 text-slate-400" />
              </label>
              <input
                type="text"
                readOnly
                disabled
                value={formData.complaint_category || ''}
                placeholder="e.g., Product Defect - Discoloration"
                className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-slate-800 cursor-not-allowed text-xs focus:outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1 flex items-center justify-between">
                <span>Defect Description</span>
                <Lock className="w-3 h-3 text-slate-400" />
              </label>
              <textarea
                readOnly
                disabled
                rows={3}
                value={formData.defect_description || ''}
                placeholder="Synthesized complaint summary will appear here..."
                className="w-full bg-white border border-slate-200 rounded-lg p-3 text-slate-800 cursor-not-allowed text-xs focus:outline-none resize-none leading-relaxed"
              />
            </div>
          </div>
        </div>

        {/* Embedded AI Copilot Risk Assessment Card */}
        <RiskAssessmentPanel />
      </div>

      {/* Bottom Button Bar: Commit to QMS Ledger */}
      <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-end">
        <button
          onClick={handleSubmitToQMS}
          disabled={loading || !!savedComplaint}
          className={`w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-lg text-sm font-bold transition-all duration-150 shadow-md ${
            savedComplaint
              ? 'bg-emerald-600 text-white cursor-default shadow-emerald-200'
              : 'bg-purple-600 hover:bg-purple-700 active:bg-purple-800 text-white disabled:opacity-50 disabled:cursor-not-allowed shadow-purple-200'
          }`}
        >
          {savedComplaint ? (
            <>
              <CheckCircle className="w-4 h-4" />
              Committed to QMS Ledger
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              {loading ? 'Committing...' : 'Commit to QMS Ledger'}
            </>
          )}
        </button>
      </div>
    </div>
  );
}

