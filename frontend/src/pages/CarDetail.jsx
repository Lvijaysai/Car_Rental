// frontend/src/pages/CarDetail.jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { carsAPI, bookingsAPI, couponsAPI } from '../api/endpoints';
import { useAuth } from '../contexts/AuthContext';

// Add this helper function outside and above the CarDetail component
const getLocalISO = (offsetMins = 0) => {
  const d = new Date();
  d.setMinutes(d.getMinutes() + offsetMins);
  const tzOffset = d.getTimezoneOffset() * 60000;
  return new Date(d.getTime() - tzOffset).toISOString().slice(0, 16);
};

export default function CarDetail() {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();

  const [car, setCar] = useState(null);
  const [loading, setLoading] = useState(true);
  const [bookingType, setBookingType] = useState('hourly');

  // FIX 1: Default to 15 mins in the future to prevent immediate "past time" errors
  const [hourlyStart, setHourlyStart] = useState(getLocalISO(15));
  const [hourlyEnd, setHourlyEnd] = useState(getLocalISO(15 + 12 * 60));
  const [dailyStart, setDailyStart] = useState('');
  const [dailyEnd, setDailyEnd] = useState('');
  const [error, setError] = useState('');

  // --- NEW: Coupon State ---
  const [couponCode, setCouponCode] = useState('');
  const [discountPercentage, setDiscountPercentage] = useState(0);
  const [couponMessage, setCouponMessage] = useState('');
  const [couponError, setCouponError] = useState('');
  const [availableCoupons, setAvailableCoupons] = useState([]);

  useEffect(() => {
    fetchCar();
    fetchCoupons();
  }, [slug]);

  const fetchCoupons = async () => {
    try {
      const response = await couponsAPI.list();
      setAvailableCoupons(response.data);
    } catch (error) {
      console.error('Error fetching coupons:', error);
    }
  };

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
      const tzOffset = end.getTimezoneOffset() * 60000;
      const localISOTime = new Date(end.getTime() - tzOffset).toISOString().slice(0, 16);

      setHourlyEnd(localISOTime);
    }
  };

  // FIX 2: Strictly auto-set end time when start changes
  const handleHourlyStartChange = (e) => {
    const newStart = e.target.value;
    setHourlyStart(newStart);

    const startDate = new Date(newStart);
    const endDate = new Date(startDate.getTime() + 12 * 60 * 60 * 1000);
    const tzOffset = endDate.getTimezoneOffset() * 60000;

    setHourlyEnd(new Date(endDate.getTime() - tzOffset).toISOString().slice(0, 16));
  };

  // --- NEW: Handle Coupon Validation ---
  const handleApplyCoupon = async () => {
    setCouponError('');
    setCouponMessage('');
    
    if (!couponCode.trim()) {
      setCouponError('Please enter a code first.');
      return;
    }

    if (!isAuthenticated) {
      setCouponError('Please login to apply coupons.');
      return;
    }

    try {
      const response = await couponsAPI.apply({ code: couponCode });
      setDiscountPercentage(response.data.discount_percentage);
      setCouponMessage(response.data.message);
    } catch (err) {
      setCouponError(err.response?.data?.error || 'Invalid coupon.');
      setDiscountPercentage(0);
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

      if (discountPercentage > 0) {
        data.coupon_code = couponCode;
      }

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

  // Calculate dynamic price display
  const getDisplayPrice = () => {
    const basePrice = bookingType === 'hourly' ? car.twelve_hour_rate : car.daily_rate;
    if (discountPercentage > 0) {
      return (basePrice - (basePrice * discountPercentage) / 100).toFixed(2);
    }
    return basePrice;
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
                <h2 className="text-2xl font-bold">
                  {car.brand} {car.name}
                </h2>

                <span className="badge bg-green-500 text-white px-3 py-1 rounded-full text-sm mt-2 inline-block">
                  {car.status}
                </span>
              </div>

              {/* Updated Price Display to handle strikethrough logic */}
              <div className="text-right">
                {discountPercentage > 0 && (
                  <div className="text-gray-400 line-through text-lg font-bold">
                    ₹{bookingType === 'hourly' ? car.twelve_hour_rate : car.daily_rate}
                  </div>
                )}
                <h3 className="text-primary font-bold text-3xl">
                  ₹{getDisplayPrice()}
                </h3>
                <small className="text-gray-600">
                  /{bookingType === 'hourly' ? '12-hours' : 'day'}
                </small>
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
                <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm font-semibold">
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
                      min={getLocalISO(0)}
                      onChange={handleHourlyStartChange}
                      className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg"
                      required
                    />
                  </div>

                  <div className="mb-4">
                    <label className="block text-sm font-bold text-gray-700 mb-2">
                      DROP-OFF TIME (12-Hour Block)
                    </label>

                    <input
                      type="datetime-local"
                      value={hourlyEnd}
                      readOnly
                      className="w-full px-4 py-3 bg-gray-200 border border-gray-200 rounded-lg text-gray-500 cursor-not-allowed"
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
                        className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg"
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
                        className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-lg"
                        required
                      />
                    </div>
                  </div>
                </>
              )}

              {/* --- Promo Code UI Section --- */}
              <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                <label className="block text-sm font-bold text-gray-700 mb-2">HAVE A PROMO CODE?</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={couponCode}
                    onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
                    placeholder="Enter code"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    disabled={discountPercentage > 0}
                  />
                  <button
                    type="button"
                    onClick={handleApplyCoupon}
                    disabled={discountPercentage > 0}
                    className="bg-gray-800 text-white px-4 py-2 rounded-lg font-bold hover:bg-gray-700 disabled:opacity-50 transition-colors"
                  >
                    {discountPercentage > 0 ? 'Applied' : 'Apply'}
                  </button>
                </div>
                
                {couponMessage && <p className="text-green-600 text-sm mt-2 font-semibold">✓ {couponMessage}</p>}
                {couponError && <p className="text-red-600 text-sm mt-2 font-semibold">✗ {couponError}</p>}

                {/* --- NEW: Available Coupons List --- */}
                {availableCoupons.length > 0 && discountPercentage === 0 && (
                  <div className="mt-4 border-t border-gray-200 pt-3">
                    <p className="text-xs text-gray-500 font-bold mb-2">AVAILABLE OFFERS:</p>
                    <div className="flex flex-wrap gap-2">
                      {availableCoupons.map((c) => (
                        <button
                          key={c.id}
                          type="button"
                          onClick={() => setCouponCode(c.code)}
                          className="text-xs bg-white border border-dashed border-primary text-primary px-3 py-1.5 rounded hover:bg-blue-50 transition-colors"
                        >
                          <span className="font-bold">{c.code}</span> ({c.discount_percentage}% OFF)
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                {/* ----------------------------------- */}
              </div>
              {/* --------------------------------- */}

              {isAuthenticated ? (
                <>
                  <button
                    type="submit"
                    className="w-full bg-primary text-white py-4 rounded-lg font-bold text-lg hover:bg-blue-600 shadow-lg mt-2 transition-colors"
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
                  className="block w-full bg-yellow-500 text-white py-4 rounded-lg font-bold text-lg hover:bg-yellow-600 shadow-lg mt-2 text-center transition-colors"
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