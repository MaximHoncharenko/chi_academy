import { configureStore } from '@reduxjs/toolkit';
import booksReducer from './booksSlice.ts';

export const store = configureStore({
  reducer: {
    books: booksReducer,
  },
});

// Типи для використання в хуках
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;