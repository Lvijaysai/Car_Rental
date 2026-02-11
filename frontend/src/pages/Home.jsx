// frontend/src/pages/Home.jsx
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-12 text-center">
      <div className="py-12">
        <h1 className="text-5xl font-bold mb-4">Welcome to Budget Car Rentals</h1>
        <p className="text-xl text-gray-600 mb-8">
          Your premium car rental experience starts here.
        </p>
        <Link
          to="/cars"
          className="inline-block bg-primary text-white px-8 py-4 rounded-full font-bold hover:bg-blue-600 shadow-lg"
        >
          View Fleet / Book Now
        </Link>
      </div>
    </div>
  );
}
