// BooksApp.tsx
import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Box,
  Chip,
  Rating,
  Checkbox,
  FormControlLabel,
  Paper,
  CardMedia,
} from '@mui/material';
import {
  ArrowBack,
  Add,
  Search,
  CheckCircle,
} from '@mui/icons-material';

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
    isRead: false,
  },
  {
    id: '2',
    name: 'Захар Беркут',
    author: 'Іван Франко',
    genre: 'Історичний роман',
    rating: 4,
    description: 'Історичний роман про боротьбу карпатських горян проти монгольської навали.',
    imgUrl: 'https://via.placeholder.com/200x300/E94B3C/ffffff?text=Книга+2',
    isRead: true,
  },
  {
    id: '3',
    name: 'Собор',
    author: 'Олесь Гончар',
    genre: 'Роман',
    rating: 5,
    description: 'Роман про духовні цінності українського народу та боротьбу за їх збереження.',
    imgUrl: 'https://via.placeholder.com/200x300/6FCF97/ffffff?text=Книга+3',
    isRead: false,
  },
];

const BooksApp: React.FC = () => {
  const [books, setBooks] = useState<Book[]>(INITIAL_BOOKS);
  const [selectedBookId, setSelectedBookId] = useState<string | null>(null);
  const [filter, setFilter] = useState({ id: '', name: '', author: '' });
  const [newBook, setNewBook] = useState({
    name: '',
    author: '',
    genre: '',
    rating: 5,
    description: '',
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

  const filteredBooks = books.filter((book) => {
    const matchesId =
      filter.id === '' || book.id.toLowerCase().includes(filter.id.toLowerCase());
    const matchesName =
      filter.name === '' || book.name.toLowerCase().includes(filter.name.toLowerCase());
    const matchesAuthor =
      filter.author === '' ||
      book.author.toLowerCase().includes(filter.author.toLowerCase());
    return matchesId && matchesName && matchesAuthor;
  });

  const handleAddBook = () => {
    if (!newBook.name || !newBook.author || !newBook.genre) {
      alert("Будь ласка, заповніть всі обов'язкові поля (ім'я, автор, жанр)");
      return;
    }

    const book: Book = {
      id: Date.now().toString(),
      name: newBook.name,
      author: newBook.author,
      genre: newBook.genre,
      rating: newBook.rating,
      description: newBook.description,
      imgUrl: `https://via.placeholder.com/200x300/${Math.floor(
        Math.random() * 16777215
      ).toString(16)}/ffffff?text=${encodeURIComponent(newBook.name.substring(0, 10))}`,
      isRead: false,
    };

    setBooks([...books, book]);
    setNewBook({ name: '', author: '', genre: '', rating: 5, description: '' });
  };

  const toggleReadStatus = (id: string) => {
    setBooks(
      books.map((book) => (book.id === id ? { ...book, isRead: !book.isRead } : book))
    );
  };

  const selectedBook = books.find((book) => book.id === selectedBookId);

  // Сторінка деталей книги
  if (selectedBook) {
    return (
      <Box sx={{ bgcolor: 'background.default', minHeight: '100vh', py: 4 }}>
        <Container maxWidth="lg">
          <Paper elevation={3} sx={{ overflow: 'hidden' }}>
            <Grid container spacing={0}>
              <Grid size={{ xs: 12, md: 4 }}>
                <CardMedia
                  component="img"
                  image={selectedBook.imgUrl}
                  alt={selectedBook.name}
                  sx={{ height: '100%', minHeight: 400, objectFit: 'cover' }}
                />
              </Grid>
              <Grid size={{ xs: 12, md: 8 }}>
                <CardContent sx={{ p: 4 }}>
                  <Typography variant="h3" component="h1" gutterBottom>
                    {selectedBook.name}
                  </Typography>
                  <Typography variant="h5" color="text.secondary" gutterBottom>
                    Автор: {selectedBook.author}
                  </Typography>

                  <Box sx={{ my: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip label={selectedBook.genre} color="primary" />
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Rating value={selectedBook.rating} readOnly />
                      <Typography variant="body2" sx={{ ml: 1 }}>
                        ({selectedBook.rating}/5)
                      </Typography>
                    </Box>
                  </Box>

                  <Typography variant="body1" paragraph sx={{ my: 3 }}>
                    {selectedBook.description}
                  </Typography>

                  <FormControlLabel
                    control={
                      <Checkbox
                        checked={selectedBook.isRead}
                        onChange={() => toggleReadStatus(selectedBook.id)}
                        icon={<CheckCircle />}
                        checkedIcon={<CheckCircle />}
                      />
                    }
                    label="Прочитано"
                    sx={{ my: 2 }}
                  />

                  <Box sx={{ mt: 4 }}>
                    <Button
                      variant="contained"
                      size="large"
                      startIcon={<ArrowBack />}
                      onClick={() => setSelectedBookId(null)}
                    >
                      Назад до списку
                    </Button>
                  </Box>
                </CardContent>
              </Grid>
            </Grid>
          </Paper>
        </Container>
      </Box>
    );
  }

  // Головна сторінка
  return (
    <Box sx={{ bgcolor: 'background.default', minHeight: '100vh', py: 4 }}>
      <Container maxWidth="xl">
        <Typography variant="h3" component="h1" align="center" gutterBottom sx={{ mb: 4 }}>
          📚 Моя Бібліотека
        </Typography>

        {/* Фільтри */}
        <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
          <Typography
            variant="h5"
            gutterBottom
            sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
          >
            <Search /> Фільтри
          </Typography>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                label="Пошук за ID"
                variant="outlined"
                value={filter.id}
                onChange={(e) => setFilter({ ...filter, id: e.target.value })}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                label="Пошук за назвою"
                variant="outlined"
                value={filter.name}
                onChange={(e) => setFilter({ ...filter, name: e.target.value })}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                label="Пошук за автором"
                variant="outlined"
                value={filter.author}
                onChange={(e) => setFilter({ ...filter, author: e.target.value })}
              />
            </Grid>
          </Grid>
        </Paper>

        {/* Форма додавання книги */}
        <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
          <Typography
            variant="h5"
            gutterBottom
            sx={{ display: 'flex', alignItems: 'center', gap: 1 }}
          >
            <Add /> Додати нову книгу
          </Typography>
          <Grid container spacing={2}>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Назва книги *"
                variant="outlined"
                value={newBook.name}
                onChange={(e) => setNewBook({ ...newBook, name: e.target.value })}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Автор *"
                variant="outlined"
                value={newBook.author}
                onChange={(e) => setNewBook({ ...newBook, author: e.target.value })}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                label="Жанр *"
                variant="outlined"
                value={newBook.genre}
                onChange={(e) => setNewBook({ ...newBook, genre: e.target.value })}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography>Рейтинг:</Typography>
                <Rating
                  value={newBook.rating}
                  onChange={(e, newValue) =>
                    setNewBook({ ...newBook, rating: newValue || 5 })
                  }
                />
              </Box>
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField
                fullWidth
                label="Опис книги"
                variant="outlined"
                multiline
                rows={3}
                value={newBook.description}
                onChange={(e) => setNewBook({ ...newBook, description: e.target.value })}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <Button
                variant="contained"
                color="success"
                size="large"
                startIcon={<Add />}
                onClick={handleAddBook}
              >
                Додати книгу
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Список книг з використанням Grid - 3 колонки: назва, автор, рейтинг */}
        <Box>
          {filteredBooks.map((book) => (
            <Paper key={book.id} elevation={2} sx={{ mb: 2, p: 2 }}>
              <Grid container spacing={2} sx={{ alignItems: 'center' }}>
                {/* Назва книги */}
                <Grid size={{ xs: 12, sm: 4 }}>
                  <Box>
                    <Typography variant="h6" component="h3" gutterBottom>
                      {book.name}
                    </Typography>
                    {book.isRead && (
                      <Chip
                        icon={<CheckCircle />}
                        label="Прочитано"
                        color="success"
                        size="small"
                      />
                    )}
                  </Box>
                </Grid>

                {/* Автор */}
                <Grid size={{ xs: 12, sm: 3 }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Автор
                    </Typography>
                    <Typography variant="body1">{book.author}</Typography>
                  </Box>
                </Grid>

                {/* Рейтинг */}
                <Grid size={{ xs: 12, sm: 3 }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Рейтинг
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Rating value={book.rating} readOnly size="small" />
                      <Typography variant="body2">{book.rating}/5</Typography>
                    </Box>
                  </Box>
                </Grid>

                {/* Кнопка деталей */}
                <Grid size={{ xs: 12, sm: 2 }}>
                  <Button
                    variant="contained"
                    onClick={() => setSelectedBookId(book.id)}
                    fullWidth
                  >
                    Деталі
                  </Button>
                </Grid>
              </Grid>
            </Paper>
          ))}
        </Box>

        {filteredBooks.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 8 }}>
            <Typography variant="h5" color="text.secondary">
              📭 Книг не знайдено
            </Typography>
          </Box>
        )}
      </Container>
    </Box>
  );
};

export default BooksApp;