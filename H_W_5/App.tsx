import React from 'react';
import BooksList from './BooksList';

const App: React.FC = () => {
  return (
    <div>
      <h1>Список книг</h1>
      <BooksList />
    </div>
  );
};

export default App;