import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const initialState = {
  formData: {
    complaint_source: '',
    customer_name: '',
    product_name: '',
    product_strength: '',
    batch_number: '',
    affected_quantity: '',
    manufacturing_date: '',
    expiry_date: '',
    originating_site_block: '',
    impacted_npm: '',
    complaint_category: '',
    defect_description: '',
  },
  riskAssessment: {
    severity: 'Not Assessed',
    suggested_next_action: '',
    initial_risk_assessment: '',
  },
  completenessScore: 0,
  messages: [
    {
      sender: 'assistant',
      text: 'Ready to process new complaints. You can paste the raw email from the customer, or upload a PDF of the complaint report. I will extract the data and run the initial risk assessment.',
    },
  ],
  loading: false,
  error: null,
  savedComplaint: null,
};

// Async thunk: Send message to conversational QMS agent
export const sendMessage = createAsyncThunk(
  'complaint/sendMessage',
  async (messageText, { getState, rejectWithValue }) => {
    try {
      const { formData, riskAssessment } = getState().complaint;
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        message: messageText,
        current_form: formData,
        current_risk: riskAssessment,
      });
      return response.data;
    } catch (err) {
      const message = err.response?.data?.detail || err.message || 'Failed to send message';
      return rejectWithValue(message);
    }
  }
);

// Async thunk: Upload PDF or text/email complaint file
export const uploadComplaintFile = createAsyncThunk(
  'complaint/uploadComplaintFile',
  async (file, { rejectWithValue }) => {
    try {
      const data = new FormData();
      data.append('file', file);
      const response = await axios.post(`${API_BASE_URL}/upload`, data, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return { ...response.data, fileName: file.name };
    } catch (err) {
      const message = err.response?.data?.detail || err.message || 'Failed to upload complaint file';
      return rejectWithValue(message);
    }
  }
);

// Async thunk: Save and finalize complaint in SQLite database (Commit to QMS Ledger)
export const saveComplaint = createAsyncThunk(
  'complaint/saveComplaint',
  async (_, { getState, rejectWithValue }) => {
    try {
      const { formData, riskAssessment, completenessScore } = getState().complaint;
      const payload = {
        ...formData,
        severity: riskAssessment.severity !== 'Not Assessed' ? riskAssessment.severity : null,
        suggested_next_action: riskAssessment.suggested_next_action || '',
        initial_risk_assessment: riskAssessment.initial_risk_assessment || '',
        completeness_score: completenessScore,
        status: 'Logged',
      };
      const response = await axios.post(`${API_BASE_URL}/complaints`, payload);
      return response.data;
    } catch (err) {
      const message = err.response?.data?.detail || err.message || 'Failed to save complaint';
      return rejectWithValue(message);
    }
  }
);

export const complaintSlice = createSlice({
  name: 'complaint',
  initialState,
  reducers: {
    updateFormField: (state, action) => {
      const { field, value } = action.payload;
      if (field in state.formData) {
        state.formData[field] = value;
      }
    },
    resetComplaintState: () => initialState,
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // sendMessage lifecycle
      .addCase(sendMessage.pending, (state, action) => {
        state.loading = true;
        state.error = null;
        state.messages.push({
          sender: 'user',
          text: action.meta.arg,
        });
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.loading = false;
        const { reply, updated_form, updated_risk, completeness_score } = action.payload;

        if (updated_form && typeof updated_form === 'object') {
          state.formData = {
            ...state.formData,
            ...updated_form,
          };
        }

        if (updated_risk && typeof updated_risk === 'object') {
          state.riskAssessment = {
            severity: updated_risk.severity || state.riskAssessment.severity,
            suggested_next_action: updated_risk.suggested_next_action || updated_risk.suggested_actions?.[0] || state.riskAssessment.suggested_next_action,
            initial_risk_assessment: updated_risk.initial_risk_assessment || updated_risk.rationale || state.riskAssessment.initial_risk_assessment,
          };
        }

        if (typeof completeness_score === 'number') {
          state.completenessScore = completeness_score;
        }

        if (reply) {
          state.messages.push({
            sender: 'assistant',
            text: reply,
          });
        }
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'An error occurred';
        state.messages.push({
          sender: 'assistant',
          text: `Error: ${state.error}`,
        });
      })

      // uploadComplaintFile lifecycle
      .addCase(uploadComplaintFile.pending, (state, action) => {
        state.loading = true;
        state.error = null;
        state.messages.push({
          sender: 'user',
          text: `Uploaded file: ${action.meta.arg.name}`,
        });
      })
      .addCase(uploadComplaintFile.fulfilled, (state, action) => {
        state.loading = false;
        const { reply, updated_form, updated_risk, completeness_score } = action.payload;

        if (updated_form && typeof updated_form === 'object') {
          state.formData = {
            ...state.formData,
            ...updated_form,
          };
        }

        if (updated_risk && typeof updated_risk === 'object') {
          state.riskAssessment = {
            severity: updated_risk.severity || state.riskAssessment.severity,
            suggested_next_action: updated_risk.suggested_next_action || updated_risk.suggested_actions?.[0] || state.riskAssessment.suggested_next_action,
            initial_risk_assessment: updated_risk.initial_risk_assessment || updated_risk.rationale || state.riskAssessment.initial_risk_assessment,
          };
        }

        if (typeof completeness_score === 'number') {
          state.completenessScore = completeness_score;
        }

        if (reply) {
          state.messages.push({
            sender: 'assistant',
            text: reply,
          });
        }
      })
      .addCase(uploadComplaintFile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to upload document';
        state.messages.push({
          sender: 'assistant',
          text: `Upload Error: ${state.error}`,
        });
      })

      // saveComplaint lifecycle
      .addCase(saveComplaint.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(saveComplaint.fulfilled, (state, action) => {
        state.loading = false;
        state.savedComplaint = action.payload;
        const recordCode = action.payload?.complaint_id || action.payload?.id;
        state.messages.push({
          sender: 'assistant',
          text: `Complaint record successfully committed to QMS Ledger (ID: ${recordCode}).`,
        });
      })
      .addCase(saveComplaint.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload || 'Failed to commit complaint to QMS Ledger';
        state.messages.push({
          sender: 'assistant',
          text: `Commit Error: ${state.error}`,
        });
      });
  },
});

export const { updateFormField, resetComplaintState, clearError } = complaintSlice.actions;
export default complaintSlice.reducer;

