// frontend/src/pages/CarList.jsx
import { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { carsAPI } from '../api/endpoints';
import { format } from 'date-fns';

export default function CarList() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [cars, setCars] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [startDate, setStartDate] = useState(searchParams.get('start') || '');
  const [endDate, setEndDate] = useState(searchParams.get('end') || '');

  useEffect(() => {
    fetchCars();
  }, [searchParams]);

  const fetchCars = async () => {
    setLoading(true);
    try {
      const params = {
        q: searchParams.get('q'),
        start: searchParams.get('start'),
        end: searchParams.get('end'),
      };
      const response = await carsAPI.list(params);
      setCars(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching cars:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (searchQuery) params.set('q', searchQuery);
    if (startDate) params.set('start', startDate);
    if (endDate) params.set('end', endDate);
    setSearchParams(params);
  };

  const getStatusBadge = (car) => {
    const colors = {
      success: 'bg-green-500',
      danger: 'bg-red-500',
      secondary: 'bg-gray-500',
      warning: 'bg-yellow-500',
    };
    return colors[car.status_color] || 'bg-gray-500';
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <div className="text-gray-500">Loading cars...</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">Find Your Perfect Drive</h1>
          <p className="text-gray-600">Choose from our luxury and economy fleet</p>
        </div>

        <div className="bg-white shadow-sm rounded-lg mb-8 p-6">
          <form onSubmit={handleSearch}>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  SEARCH
                </label>
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Brand or Model..."
                  className="w-full px-4 py-3 bg-gray-50 border-0 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  PICK-UP
                </label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-50 border-0 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-2">
                  DROP-OFF
                </label>
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                  className="w-full px-4 py-3 bg-gray-50 border-0 rounded-lg"
                />
              </div>
              <div className="flex items-end">
                <button
                  type="submit"
                  className="w-full bg-primary text-white px-6 py-3 rounded-lg font-bold hover:bg-blue-600"
                >
                  Check Availability
                </button>
              </div>
            </div>
          </form>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {cars.length === 0 ? (
            <div className="col-span-3 text-center py-12">
              <h3 className="text-gray-500 text-xl">No cars available yet 🚗</h3>
              <p className="text-gray-400 mt-2">
                Login to the Admin panel to add your first vehicle!
              </p>
            </div>
          ) : (
            cars.map((car) => (
              <div
                key={car.id}
                className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-lg transition-shadow"
              >
                <div className="relative">
                  {car.image && (
                    <img
                      src={car.image}
                      alt={car.name}
                      className="w-full h-56 object-cover"
                    />
                  )}
                  <span className="absolute top-3 left-3 bg-white text-gray-900 px-3 py-1 rounded-full text-sm font-bold">
                    {car.category_name}
                  </span>
                  <span
                    className={`absolute top-3 right-3 ${getStatusBadge(car)} text-white px-3 py-1 rounded-full text-sm font-bold`}
                  >
                    {car.live_status}
                  </span>
                </div>
                <div className="p-6">
                  <div className="flex justify-between items-center mb-2">
                    <h5 className="font-bold text-lg">{car.brand} {car.name}</h5>
                    <span className="text-primary font-bold">
                      ₹{car.daily_rate}/day
                    </span>
                  </div>
                  <div className="flex justify-between text-gray-600 text-sm mb-4">
                    <span>⚙️ {car.transmission}</span>
                    <span>⛽ {car.fuel_type}</span>
                    <span>💺 {car.seats} Seats</span>
                  </div>
                  {car.status === 'MAINTENANCE' ? (
                    <button
                      className="w-full bg-gray-400 text-white py-2 rounded-lg"
                      disabled
                    >
                      Under Maintenance
                    </button>
                  ) : (
                    <Link
                      to={`/cars/${car.slug}`}
                      className="block w-full bg-gray-900 text-white py-2 rounded-lg text-center hover:bg-gray-800"
                    >
                      {car.is_available ? 'Book Now' : 'Check Availability'}
                    </Link>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
