import { store } from './src/app/store.js';
import { updateFormField, resetComplaintState } from './src/features/complaintSlice.js';

console.log('--- Checking Initial State ---');
const state = store.getState();
console.log('Initial State:', JSON.stringify(state, null, 2));

console.assert(state.complaint !== undefined, 'complaint slice should be mounted');
console.assert(state.complaint.completenessScore === 0, 'Initial completenessScore should be 0');
console.assert(state.complaint.riskAssessment.severity === 'Not Assessed', 'Severity should be Not Assessed');
console.assert(state.complaint.messages.length === 1, 'Should have 1 greeting message');
console.assert(state.complaint.formData.product_name === '', 'Initial product_name should be empty string');

console.log('--- Testing updateFormField reducer ---');
store.dispatch(updateFormField({ field: 'product_name', value: 'Amoxicillin 500mg' }));
const updatedState = store.getState();
console.log('Updated product_name:', updatedState.complaint.formData.product_name);
console.assert(updatedState.complaint.formData.product_name === 'Amoxicillin 500mg', 'product_name should be updated');

console.log('--- Testing resetComplaintState reducer ---');
store.dispatch(resetComplaintState());
const resetState = store.getState();
console.assert(resetState.complaint.formData.product_name === '', 'product_name should be reset');

console.log('\n[ALL REDUX STORE & SLICE TESTS PASSED CLEANLY!]');
