// frontend/src/pages/BookingSuccess.jsx
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { bookingsAPI } from '../api/endpoints';
import { format } from 'date-fns';

export default function BookingSuccess() {
  const { id } = useParams();
  const [booking, setBooking] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBooking();
  }, [id]);

  const fetchBooking = async () => {
    try {
      const response = await bookingsAPI.list();
      const found = response.data.results?.find(b => b.id === parseInt(id)) ||
                    response.data.find(b => b.id === parseInt(id));
      setBooking(found);
    } catch (error) {
      console.error('Error fetching booking:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    );
  }

  if (!booking) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <div className="text-red-500">Booking not found</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-2xl mx-auto text-center">
        <div className="mb-6">
          <div className="text-green-500 text-6xl mb-4">✓</div>
        </div>

        <h1 className="text-4xl font-bold mb-4">Request Received!</h1>
        <p className="text-lg text-gray-600 mb-8">
          You have requested the <strong>{booking.car.brand} {booking.car.name}</strong>{' '}
          from {format(new Date(booking.start_time), 'MMM d, yyyy HH:mm')} to{' '}
          {format(new Date(booking.end_time), 'MMM d, yyyy HH:mm')}.
        </p>

        <div className="bg-yellow-50 border-2 border-yellow-400 rounded-lg p-6 mb-6">
          <h4 className="font-bold text-lg mb-2">⚠️ One Final Step</h4>
          <p className="mb-4">
            To finalize your reservation and arrange payment, please call our admin team.
            Your Booking ID is <strong>#{booking.id}</strong>.
          </p>
          <a
            href="tel:+919876543210"
            className="inline-block bg-gray-900 text-white px-8 py-3 rounded-full font-bold hover:bg-gray-800"
          >
            📞 Call +91 987 654 3210
          </a>
        </div>

        <Link
          to="/dashboard"
          className="text-primary hover:underline"
        >
          ← Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
