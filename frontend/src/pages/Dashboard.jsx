// frontend/src/pages/Dashboard.jsx
import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { dashboardAPI, bookingsAPI } from '../api/endpoints';
import { format } from 'date-fns';

export default function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await dashboardAPI.dashboard();
      setDashboardData(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async (bookingId) => {
    if (!window.confirm('Are you sure you want to cancel this booking?')) {
      return;
    }

    try {
      await bookingsAPI.cancel(bookingId);
      fetchDashboard(); // Refresh data
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to cancel booking');
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <div className="text-gray-500">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold">My Dashboard</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-50 rounded-lg p-6 text-center">
          <div className="w-16 h-16 bg-primary text-white rounded-full flex items-center justify-center font-bold text-2xl mx-auto mb-3">
            {dashboardData?.user?.username?.[0]?.toUpperCase() || 'U'}
          </div>
          <h5 className="font-bold mb-1">{dashboardData?.user?.username}</h5>
          <p className="text-gray-600 text-sm mb-4">
            Member since {dashboardData?.user?.date_joined ? format(new Date(dashboardData.user.date_joined), 'MMM yyyy') : 'N/A'}
          </p>
          <Link
            to="/history"
            className="inline-block bg-gray-900 text-white px-4 py-2 rounded-full text-sm hover:bg-gray-800"
          >
            View Booking History
            {dashboardData?.history_count > 0 && (
              <span className="ml-2 bg-gray-600 px-2 py-1 rounded-full">
                {dashboardData.history_count}
              </span>
            )}
          </Link>
        </div>

        <div className="md:col-span-3">
          <h4 className="font-bold mb-4 text-primary text-xl">Active Bookings</h4>
          {dashboardData?.active_bookings?.length === 0 ? (
            <div className="bg-gray-50 border-2 border-dashed rounded-lg py-12 text-center">
              <p className="text-gray-500 mb-4">No active bookings found.</p>
              <Link
                to="/cars"
                className="inline-block bg-primary text-white px-6 py-2 rounded-lg hover:bg-blue-600"
              >
                Book a Car
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {dashboardData?.active_bookings?.map((booking) => (
                <div
                  key={booking.id}
                  className="bg-white rounded-lg shadow-sm p-6"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h5 className="font-bold text-lg mb-1">
                        {booking.car.brand} {booking.car.name}
                      </h5>
                      <p className="text-gray-600 text-sm mb-2">
                        {format(new Date(booking.start_time), 'MMM d, yyyy HH:mm')} →{' '}
                        {format(new Date(booking.end_time), 'MMM d, yyyy HH:mm')}
                      </p>
                      <span
                        className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
                          booking.status === 'APPROVED'
                            ? 'bg-green-500 text-white'
                            : 'bg-yellow-500 text-gray-900'
                        }`}
                      >
                        {booking.status_display}
                      </span>
                    </div>
                    <div className="text-right">
                      <h4 className="text-primary font-bold text-2xl mb-2">
                        ₹{booking.total_price}
                      </h4>
                      <button
                        onClick={() => handleCancel(booking.id)}
                        className="text-red-600 hover:text-red-800 text-sm font-semibold"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                  {booking.status === 'PENDING' && (
                    <div className="mt-4 bg-yellow-50 text-yellow-800 p-3 rounded-lg text-sm">
                      ⚠️ Please call to confirm this booking.
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
