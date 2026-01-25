import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from './store';
import { fetchBooks } from './booksSlice';

const BooksList: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { items, loading, error } = useSelector((state: RootState) => state.books);

  useEffect(() => {
    dispatch(fetchBooks());
  }, [dispatch]);

  if (loading) return <p>Завантаження...</p>;
  if (error) return <p>Помилка: {error}</p>;

  return (
    <ul>
      {items.map((book) => (
        <li key={book.id}>
          <strong>{book.title}</strong> — {book.author}
        </li>
      ))}
    </ul>
  );
};

export default BooksList;