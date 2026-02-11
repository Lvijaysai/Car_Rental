// frontend/src/pages/Register.jsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Register() {
  const [formData, setFormData] = useState({
    username: '',
    password1: '',
    password2: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setLoading(true);

    const result = await register(formData);
    if (result.success) {
      navigate('/login');
    } else {
      setErrors(result.errors || {});
    }
    setLoading(false);
  };

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-lg mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-8">
          <div className="text-center mb-6">
            <h3 className="text-2xl font-bold mb-2">Create Account</h3>
            <p className="text-gray-600">Join Budget Car Rentals today</p>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block mb-2 font-semibold text-sm">Username</label>
              <input
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-50 border-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                required
              />
              {errors.username && (
                <div className="text-red-600 text-sm mt-1">{errors.username[0]}</div>
              )}
            </div>

            <div className="mb-4">
              <label className="block mb-2 font-semibold text-sm">Password</label>
              <input
                type="password"
                name="password1"
                value={formData.password1}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-50 border-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                required
              />
              {errors.password1 && (
                <div className="text-red-600 text-sm mt-1">{errors.password1[0]}</div>
              )}
            </div>

            <div className="mb-6">
              <label className="block mb-2 font-semibold text-sm">Confirm Password</label>
              <input
                type="password"
                name="password2"
                value={formData.password2}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-50 border-0 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                required
              />
              {errors.password2 && (
                <div className="text-red-600 text-sm mt-1">{errors.password2[0]}</div>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-white py-2 rounded-lg font-semibold hover:bg-blue-600 disabled:opacity-50"
            >
              {loading ? 'Creating account...' : 'Sign Up'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-primary font-semibold hover:underline">
              Login here
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
