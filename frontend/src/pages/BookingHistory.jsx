// frontend/src/pages/BookingHistory.jsx
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardAPI } from '../api/endpoints';
import { format } from 'date-fns';

export default function BookingHistory() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await dashboardAPI.history();
      setBookings(response.data.bookings);
    } catch (error) {
      console.error('Error fetching history:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <div className="text-gray-500">Loading history...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold">Booking History</h2>
        <Link
          to="/dashboard"
          className="text-gray-600 hover:text-primary"
        >
          ← Back to Dashboard
        </Link>
      </div>

      {bookings.length === 0 ? (
        <div className="bg-gray-50 rounded-lg py-12 text-center">
          <div className="text-4xl mb-3">📜</div>
          <h5 className="font-bold text-lg mb-2">No history yet</h5>
          <p className="text-gray-600">
            You haven't completed or cancelled any trips.
          </p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-4 text-left text-sm font-bold">Car</th>
                  <th className="px-6 py-4 text-left text-sm font-bold">Dates</th>
                  <th className="px-6 py-4 text-left text-sm font-bold">Total</th>
                  <th className="px-6 py-4 text-left text-sm font-bold">Status</th>
                  <th className="px-6 py-4 text-right text-sm font-bold">Booked On</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {bookings.map((booking) => (
                  <tr key={booking.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-bold text-gray-700">
                      {booking.car.brand} {booking.car.name}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      {format(new Date(booking.start_time), 'MMM d, HH:mm')} →{' '}
                      {format(new Date(booking.end_time), 'MMM d, HH:mm')}
                    </td>
                    <td className="px-6 py-4 font-bold">₹{booking.total_price}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-sm ${
                          booking.status === 'COMPLETED'
                            ? 'bg-gray-500 text-white'
                            : 'bg-red-100 text-red-600'
                        }`}
                      >
                        {booking.status_display}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right text-sm text-gray-600">
                      {format(new Date(booking.created_at), 'MMM d, yyyy')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
