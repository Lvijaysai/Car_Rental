// frontend/src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import CarList from './pages/CarList';
import CarDetail from './pages/CarDetail';
import Dashboard from './pages/Dashboard';
import BookingHistory from './pages/BookingHistory';
import BookingSuccess from './pages/BookingSuccess';
import Login from './pages/Login';
import Register from './pages/Register';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen flex flex-col">
          <Navbar />
          <main className="flex-grow">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/cars" element={<CarList />} />
              <Route path="/cars/:slug" element={<CarDetail />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/history" element={<BookingHistory />} />
              <Route path="/booking/:id/success" element={<BookingSuccess />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuthProvider>
  );
}

function Footer() {
  return (
    <footer className="bg-gray-900 text-white py-12 mt-auto">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h5 className="font-bold mb-3">Budget Car Rentals</h5>
            <p className="text-gray-400 text-sm">
              Experience the thrill of the road with our premium fleet. 
              Reliable, luxurious, and affordable.
            </p>
          </div>
          <div>
            <h5 className="font-bold mb-3">Contact Us</h5>
            <ul className="text-gray-400 text-sm space-y-2">
              <li>📍 123 Main Street, Karimnagar</li>
              <li>📞 +91 987 654 3210</li>
              <li>✉️ support@budgetrentals.com</li>
            </ul>
          </div>
          <div>
            <h5 className="font-bold mb-3">Opening Hours</h5>
            <ul className="text-gray-400 text-sm space-y-1">
              <li>Mon - Sat: 9:00 AM - 8:00 PM</li>
              <li>Sunday: Closed</li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400 text-sm">
          &copy; 2024 Budget Car Rentals. All rights reserved.
        </div>
      </div>
    </footer>
  );
}

export default App;