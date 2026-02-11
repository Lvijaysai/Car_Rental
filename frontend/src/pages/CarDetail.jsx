// frontend/src/pages/CarDetail.jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { carsAPI, bookingsAPI } from '../api/endpoints';
import { useAuth } from '../contexts/AuthContext';
import { format } from 'date-fns';

export default function CarDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [car, setCar] = useState(null);
  const [loading, setLoading] = useState(true);
  const [bookingType, setBookingType] = useState('hourly');
  const [hourlyStart, setHourlyStart] = useState('');
  const [hourlyEnd, setHourlyEnd] = useState('');
  const [dailyStart, setDailyStart] = useState('');
  const [dailyEnd, setDailyEnd] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCar();
  }, [slug]);

  const fetchCar = async () => {
    try {
      const response = await carsAPI.detail(slug);
      setCar(response.data);
    } catch (error) {
      console.error('Error fetching car:', error);
    } finally {
      setLoading(false);
    }
  };

  const autoCalculateDropoff = () => {
    if (hourlyStart) {
      const start = new Date(hourlyStart);
      const end = new Date(start.getTime() + 12 * 60 * 60 * 1000);
      setHourlyEnd(end.toISOString().slice(0, 16));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!isAuthenticated) {
      navigate(`/login?next=/cars/${slug}`);
      return;
    }

    try {
      const data = {
        car_slug: slug,
        booking_type: bookingType,
      };

      if (bookingType === 'hourly') {
        if (!hourlyStart || !hourlyEnd) {
          setError('Please select both Pick-up and Drop-off times.');
          return;
        }
        const start = new Date(hourlyStart);
        const end = new Date(hourlyEnd);
        const diffHours = (end - start) / 1000 / 60 / 60;
        if (diffHours < 12) {
          setError('For 12-Hour Shift, the duration must be at least 12 hours.');
          return;
        }
        data.hourly_start = hourlyStart;
        data.hourly_end = hourlyEnd;
      } else {
        if (!dailyStart || !dailyEnd) {
          setError('Please select Start and End dates.');
          return;
        }
        if (dailyEnd <= dailyStart) {
          setError('End date must be after Start date.');
          return;
        }
        data.daily_start = dailyStart;
        data.daily_end = dailyEnd;
      }

      const response = await bookingsAPI.create(data);
      navigate(`/booking/${response.data.id}/success`);
    } catch (error) {
      setError(
        error.response?.data?.error ||
        error.response?.data?.message ||
        'Booking failed. Please try again.'
      );
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <div className="text-gray-500">Loading car details...</div>
      </div>
    );
  }

  if (!car) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <div className="text-red-500">Car not found</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          {car.image && (
            <img
              src={car.image}
              alt={car.name}
              className="w-full rounded-lg shadow-lg mb-6"
            />
          )}
          <h4 className="font-bold mb-4 text-xl">Vehicle Features</h4>
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-50 p-4 rounded-lg text-center">
              <small className="text-gray-600 block">Transmission</small>
              <span className="font-bold">{car.transmission}</span>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg text-center">
              <small className="text-gray-600 block">Fuel Type</small>
              <span className="font-bold">{car.fuel_type}</span>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg text-center">
              <small className="text-gray-600 block">Passengers</small>
              <span className="font-bold">{car.seats} Seats</span>
            </div>
          </div>
          <div className="bg-gray-50 p-6 rounded-lg">
            <h5 className="font-bold mb-2">Description</h5>
            <p className="text-gray-600">{car.features}</p>
          </div>
        </div>

        <div className="sticky top-20">
          <div className="bg-white shadow-lg rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-2xl font-bold">{car.brand} {car.name}</h2>
                <span className="badge bg-green-500 text-white px-3 py-1 rounded-full text-sm mt-2">
                  {car.status}
                </span>
              </div>
              <div className="text-right">
                <h3 className="text-primary font-bold text-2xl">₹{car.daily_rate}</h3>
                <small className="text-gray-600">/day</small>
              </div>
            </div>

            <hr className="my-4" />

            <div className="flex gap-2 mb-4 bg-gray-100 p-1 rounded-full">
              <button
                type="button"
                onClick={() => setBookingType('hourly')}
                className={`flex-1 py-2 rounded-full font-bold ${
                  bookingType === 'hourly'
                    ? 'bg-primary text-white'
                    : 'text-gray-700'
                }`}
              >
                ⏱️ 12-Hour Shift
              </button>
              <button
                type="button"
                onClick={() => setBookingType('daily')}
                className={`flex-1 py-2 rounded-full font-bold ${
                  bookingType === 'daily'
                    ? 'bg-primary text-white'
                    : 'text-gray-700'
                }`}
              >
                📅 Daily Rental
              </button>
            </div>

            <form onSubmit={handleSubmit}>
              {error && (
                <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">
                  {error}
                </div>
              )}

              {bookingType === 'hourly' ? (
                <>
                  <div className="bg-blue-50 text-blue-800 p-2 rounded-lg mb-4 text-sm">
                    <span className="font-semibold">Min duration:</span> 12 Hours
                  </div>
                  <div className="mb-4">
                    <label className="block text-sm font-bold text-gray-700 mb-2">
                      PICK-UP TIME
                    </label>
                    <input
                      type="datetime-local"
                      value={hourlyStart}
                      onChange={(e) => {
                        setHourlyStart(e.target.value);
                        autoCalculateDropoff();
                      }}
                      className="w-full px-4 py-3 bg-gray-50 border-0 rounded-lg"
                      required
                    />
                  </div>
                  <div className="mb-4">
                    <label className="block text-sm font-bold text-gray-700 mb-2">
                      DROP-OFF TIME
                    </label>
                    <input
                      type="datetime-local"
                      value={hourlyEnd}
                      onChange={(e) => setHourlyEnd(e.target.value)}
                      min={hourlyStart}
                      className="w-full px-4 py-3 bg-gray-50 border-0 rounded-lg"
                      required
                    />
                  </div>
                </>
              ) : (
                <>
                  <div className="bg-blue-50 text-blue-800 p-2 rounded-lg mb-4 text-sm">
                    <span className="font-semibold">Standard Pickup:</span> 9:00 AM
                  </div>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <label className="block text-sm font-bold text-gray-700 mb-2">
                        START DATE
                      </label>
                      <input
                        type="date"
                        value={dailyStart}
                        onChange={(e) => setDailyStart(e.target.value)}
                        className="w-full px-4 py-3 bg-gray-50 border-0 rounded-lg"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-gray-700 mb-2">
                        END DATE
                      </label>
                      <input
                        type="date"
                        value={dailyEnd}
                        onChange={(e) => setDailyEnd(e.target.value)}
                        min={dailyStart}
                        className="w-full px-4 py-3 bg-gray-50 border-0 rounded-lg"
                        required
                      />
                    </div>
                  </div>
                </>
              )}

              {isAuthenticated ? (
                <>
                  <button
                    type="submit"
                    className="w-full bg-primary text-white py-3 rounded-lg font-bold hover:bg-blue-600 shadow-lg mt-2"
                  >
                    Proceed to Booking
                  </button>
                  <p className="text-center text-gray-500 text-sm mt-3">
                    You won't be charged yet
                  </p>
                </>
              ) : (
                <a
                  href={`/login?next=/cars/${slug}`}
                  className="block w-full bg-yellow-500 text-white py-3 rounded-lg font-bold hover:bg-yellow-600 shadow-lg mt-2 text-center"
                >
                  Login to Book
                </a>
              )}
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
