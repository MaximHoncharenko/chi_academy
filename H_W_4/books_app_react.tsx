import React, { useState, useEffect, useRef } from 'react';
import { Star, StarOff, ArrowLeft, Plus, Search, CheckCircle } from 'lucide-react';

interface Book {
  id: string;
  name: string;
  author: string;
  genre: string;
  rating: number;
  description: string;
  imgUrl: string;
  isRead: boolean;
}

// Початкові дані книг винесені окремо для читабельності
const INITIAL_BOOKS: Book[] = [
  {
    id: '1',
    name: 'Тіні забутих предків',
    author: 'Михайло Коцюбинський',
    genre: 'Повість',
    rating: 5,
    description: 'Класична українська повість про кохання Івана та Марічки в Карпатах.',
    imgUrl: 'https://via.placeholder.com/200x300/4A90E2/ffffff?text=Книга+1',
    isRead: false
  },
  {
    id: '2',
    name: 'Захар Беркут',
    author: 'Іван Франко',
    genre: 'Історичний роман',
    rating: 4,
    description: 'Історичний роман про боротьбу карпатських горян проти монгольської навали.',
    imgUrl: 'https://via.placeholder.com/200x300/E94B3C/ffffff?text=Книга+2',
    isRead: true
  },
  {
    id: '3',
    name: 'Собор',
    author: 'Олесь Гончар',
    genre: 'Роман',
    rating: 5,
    description: 'Роман про духовні цінності українського народу та боротьбу за їх збереження.',
    imgUrl: 'https://via.placeholder.com/200x300/6FCF97/ffffff?text=Книга+3',
    isRead: false
  }
];

const StarRating = ({ rating, editable = false, onChange }: { rating: number; editable?: boolean; onChange?: (rating: number) => void }) => {
  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          onClick={() => editable && onChange && onChange(star)}
          disabled={!editable}
          className={editable ? 'cursor-pointer' : 'cursor-default'}
        >
          {star <= rating ? (
            <Star className="w-5 h-5 fill-yellow-400 text-yellow-400" />
          ) : (
            <StarOff className="w-5 h-5 text-gray-300" />
          )}
        </button>
      ))}
    </div>
  );
};

const BooksApp = () => {
  const [books, setBooks] = useState<Book[]>(INITIAL_BOOKS);
  const [selectedBookId, setSelectedBookId] = useState<string | null>(null);
  const [filter, setFilter] = useState({ id: '', name: '', author: '' });
  const [newBook, setNewBook] = useState({
    name: '',
    author: '',
    genre: '',
    rating: 5,
    description: ''
  });

  const isMounted = useRef(false);
  const prevBooks = useRef(books);
  const prevFilter = useRef(filter);
  const prevSelectedBookId = useRef(selectedBookId);

  // componentDidMount - окремий useEffect
  useEffect(() => {
    console.log('✅ Компонент BooksApp змонтовано');
    isMounted.current = true;
  }, []);

  // componentDidUpdate для books - окремий useEffect
  useEffect(() => {
    if (!isMounted.current) return;
    
    if (prevBooks.current !== books) {
      console.log('📚 Список книг оновлено:', books);
      prevBooks.current = books;
    }
  }, [books]);

  // componentDidUpdate для filter - окремий useEffect
  useEffect(() => {
    if (!isMounted.current) return;
    
    if (JSON.stringify(prevFilter.current) !== JSON.stringify(filter)) {
      console.log('🔍 Фільтр змінено:', filter);
      prevFilter.current = filter;
    }
  }, [filter]);

  // componentDidUpdate для selectedBookId - окремий useEffect
  useEffect(() => {
    if (!isMounted.current) return;
    
    if (prevSelectedBookId.current !== selectedBookId) {
      console.log('📖 Навігація: selectedBookId змінено на', selectedBookId);
      prevSelectedBookId.current = selectedBookId;
    }
  }, [selectedBookId]);

  const filteredBooks = books.filter(book => {
    const matchesId = filter.id === '' || book.id.toLowerCase().includes(filter.id.toLowerCase());
    const matchesName = filter.name === '' || book.name.toLowerCase().includes(filter.name.toLowerCase());
    const matchesAuthor = filter.author === '' || book.author.toLowerCase().includes(filter.author.toLowerCase());
    return matchesId && matchesName && matchesAuthor;
  });

  const handleAddBook = () => {
    if (!newBook.name || !newBook.author || !newBook.genre) {
      alert('Будь ласка, заповніть всі обов\'язкові поля (ім\'я, автор, жанр)');
      return;
    }

    const book: Book = {
      id: Date.now().toString(),
      name: newBook.name,
      author: newBook.author,
      genre: newBook.genre,
      rating: newBook.rating,
      description: newBook.description,
      imgUrl: `https://via.placeholder.com/200x300/${Math.floor(Math.random()*16777215).toString(16)}/ffffff?text=${encodeURIComponent(newBook.name.substring(0, 10))}`,
      isRead: false
    };

    setBooks([...books, book]);
    setNewBook({ name: '', author: '', genre: '', rating: 5, description: '' });
  };

  const toggleReadStatus = (id: string) => {
    setBooks(books.map(book => 
      book.id === id ? { ...book, isRead: !book.isRead } : book
    ));
  };

  const selectedBook = books.find(book => book.id === selectedBookId);

  // Сторінка деталей книги
  if (selectedBook) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="bg-white rounded-xl shadow-2xl overflow-hidden">
            <div className="grid grid-cols-1 md:grid-cols-3">
              <div className="bg-gray-100 p-6 flex items-center justify-center">
                <img 
                  src={selectedBook.imgUrl} 
                  alt={selectedBook.name}
                  className="rounded-lg shadow-lg max-h-96"
                />
              </div>
              <div className="md:col-span-2 p-8">
                <h1 className="text-4xl font-bold text-gray-800 mb-2">{selectedBook.name}</h1>
                <p className="text-xl text-gray-600 mb-4">Автор: {selectedBook.author}</p>
                
                <div className="flex items-center gap-3 mb-4">
                  <span className="inline-block bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm font-semibold">
                    {selectedBook.genre}
                  </span>
                  <div className="flex items-center gap-2">
                    <StarRating rating={selectedBook.rating} />
                    <span className="text-gray-600">({selectedBook.rating}/5)</span>
                  </div>
                </div>

                <p className="text-gray-700 mb-6 leading-relaxed text-lg">{selectedBook.description}</p>

                <div className="flex items-center mb-6">
                  <input
                    type="checkbox"
                    id="isRead"
                    checked={selectedBook.isRead}
                    onChange={() => toggleReadStatus(selectedBook.id)}
                    className="w-5 h-5 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
                  />
                  <label htmlFor="isRead" className="ml-2 text-gray-700 font-medium flex items-center gap-1">
                    <CheckCircle className="w-5 h-5" />
                    Прочитано
                  </label>
                </div>

                <button
                  onClick={() => setSelectedBookId(null)}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-lg transition duration-200 shadow-lg flex items-center gap-2"
                >
                  <ArrowLeft className="w-5 h-5" />
                  Назад до списку
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Головна сторінка з Grid Layout
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center">📚 Моя Бібліотека</h1>

        {/* Фільтри */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Search className="w-6 h-6" />
            Фільтри
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input
              type="text"
              placeholder="Пошук за ID"
              value={filter.id}
              onChange={(e) => setFilter({ ...filter, id: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <input
              type="text"
              placeholder="Пошук за назвою"
              value={filter.name}
              onChange={(e) => setFilter({ ...filter, name: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <input
              type="text"
              placeholder="Пошук за автором"
              value={filter.author}
              onChange={(e) => setFilter({ ...filter, author: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Форма додавання книги */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Plus className="w-6 h-6" />
            Додати нову книгу
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <input
              type="text"
              placeholder="Назва книги *"
              value={newBook.name}
              onChange={(e) => setNewBook({ ...newBook, name: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <input
              type="text"
              placeholder="Автор *"
              value={newBook.author}
              onChange={(e) => setNewBook({ ...newBook, author: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <input
              type="text"
              placeholder="Жанр *"
              value={newBook.genre}
              onChange={(e) => setNewBook({ ...newBook, genre: e.target.value })}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <div className="flex items-center gap-2">
              <label className="text-gray-700 font-medium">Рейтинг:</label>
              <StarRating 
                rating={newBook.rating} 
                editable 
                onChange={(rating) => setNewBook({ ...newBook, rating })}
              />
            </div>
          </div>
          <textarea
            placeholder="Опис книги"
            value={newBook.description}
            onChange={(e) => setNewBook({ ...newBook, description: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent mb-4"
            rows={3}
          />
          <button
            onClick={handleAddBook}
            className="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded-lg transition duration-200 shadow-lg flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Додати книгу
          </button>
        </div>

        {/* Список книг з Grid Layout - 3 колонки: назва, автор, рейтинг */}
        <div className="space-y-4">
          {filteredBooks.map(book => (
            <div key={book.id} className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-2xl transition duration-300">
              <div className="grid grid-cols-1 sm:grid-cols-12 gap-4 p-6">
                {/* Назва книги - 4 колонки */}
                <div className="sm:col-span-4 flex flex-col justify-center">
                  <h3 className="text-xl font-bold text-gray-800 mb-2">{book.name}</h3>
                  {book.isRead && (
                    <span className="inline-flex items-center gap-1 bg-green-100 text-green-800 text-xs font-semibold px-2 py-1 rounded w-fit">
                      <CheckCircle className="w-4 h-4" />
                      Прочитано
                    </span>
                  )}
                </div>

                {/* Автор - 3 колонки */}
                <div className="sm:col-span-3 flex flex-col justify-center">
                  <p className="text-sm text-gray-500 mb-1">Автор</p>
                  <p className="text-gray-700 font-medium">{book.author}</p>
                </div>

                {/* Рейтинг - 3 колонки */}
                <div className="sm:col-span-3 flex flex-col justify-center">
                  <p className="text-sm text-gray-500 mb-1">Рейтинг</p>
                  <div className="flex items-center gap-2">
                    <StarRating rating={book.rating} />
                    <span className="text-gray-600 text-sm">{book.rating}/5</span>
                  </div>
                </div>

                {/* Кнопка деталей - 2 колонки */}
                <div className="sm:col-span-2 flex items-center justify-end">
                  <button
                    onClick={() => setSelectedBookId(book.id)}
                    className="w-full sm:w-auto bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-6 rounded-lg transition duration-200"
                  >
                    Деталі →
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredBooks.length === 0 && (
          <div className="text-center py-12">
            <p className="text-2xl text-gray-500">📭 Книг не знайдено</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default BooksApp;