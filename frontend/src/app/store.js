import { configureStore } from '@reduxjs/toolkit';
import complaintReducer from '../features/complaintSlice.js';


export const store = configureStore({
  reducer: {
    complaint: complaintReducer,
  },
});

export default store;
