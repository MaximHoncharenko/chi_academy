import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export interface Book {
  id: number;
  title: string;
  author: string;
}

interface BooksState {
  items: Book[];
  loading: boolean;
  error: string | null;
}

const initialState: BooksState = {
  items: [],
  loading: false,
  error: null,
};

// Асинхронна дія (thunk) для отримання книг
export const fetchBooks = createAsyncThunk<Book[]>(
  'books/fetchBooks',
  async () => {
    const response = await fetch('https://example.com/api/books');
    if (!response.ok) {
      throw new Error('Помилка завантаження книг');
    }
    return await response.json();
  }
);

const booksSlice = createSlice({
  name: 'books',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchBooks.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchBooks.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchBooks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Помилка';
      });
  },
});

export default booksSlice.reducer;