import React, { useState, useEffect } from 'react';
import useAuth from '../hooks/useAuth';
import userService from '../services/userService';
import { formatApiError } from '../services/api';
import { getRoleBadgeClass } from '../utils/helpers';
import Loading from '../components/Loading';
import { User, Mail, Shield, Phone, MapPin, Save, CheckCircle, AlertCircle } from 'lucide-react';

export const Profile = () => {
  const { user, setUser } = useAuth();
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    address: '',
    email: '',
    role: '',
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setLoading(true);
        setErrorMsg('');
        const profile = await userService.getProfile();
        setFormData({
          name: profile.name || user?.name || '',
          phone: profile.phone || user?.phone || '',
          address: profile.address || user?.address || '',
          email: profile.email || user?.email || '',
          role: profile.role || user?.role || 'USER',
        });
      } catch (err) {
        // Fallback to local session data if offline
        setFormData({
          name: user?.name || '',
          phone: user?.phone || '',
          address: user?.address || '',
          email: user?.email || '',
          role: user?.role || 'USER',
        });
        setErrorMsg(formatApiError(err, 'Failed to retrieve profile from server. Showing cached session data.'));
      } finally {
        setLoading(false);
      }
    };

    loadProfile();
  }, [user]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setSuccessMsg('');
    setErrorMsg('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSuccessMsg('');
    setErrorMsg('');

    try {
      const updated = await userService.updateProfile({
        name: formData.name,
        phone: formData.phone,
        address: formData.address,
      });

      // Update state and auth context
      const updatedUser = {
        ...user,
        name: formData.name,
        phone: formData.phone,
        address: formData.address,
      };
      if (setUser) setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));

      setSuccessMsg(updated?.message || 'Profile updated successfully!');
    } catch (err) {
      setErrorMsg(formatApiError(err, 'Failed to update profile.'));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <Loading message="Loading profile information..." />;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">My Profile</h1>
          <p className="page-subtitle">Manage your account information and preferences</p>
        </div>
      </div>

      <div className="profile-layout" style={{ display: 'grid', gridTemplateColumns: 'minmax(280px, 320px) 1fr', gap: '1.5rem' }}>
        {/* Profile Card Summary */}
        <div className="card text-center" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '2rem 1.5rem' }}>
          <div
            className="user-avatar"
            style={{ width: '80px', height: '80px', fontSize: '2rem', borderRadius: '50%', marginBottom: '1rem' }}
          >
            <User size={40} />
          </div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.25rem' }}>
            {formData.name || 'User'}
          </h2>
          <p className="text-muted text-sm mb-3">{formData.email}</p>
          <span className={`badge ${getRoleBadgeClass(formData.role)}`} style={{ padding: '0.4rem 0.85rem' }}>
            <Shield size={12} style={{ marginRight: '4px' }} />
            {formData.role} Role
          </span>
        </div>

        {/* Edit Form */}
        <div className="card">
          <h2 className="card-title mb-3">Edit Profile Details</h2>

          {successMsg && (
            <div className="alert alert-success">
              <CheckCircle size={16} />
              <span>{successMsg}</span>
            </div>
          )}

          {errorMsg && (
            <div className="alert alert-error">
              <AlertCircle size={16} />
              <span>{errorMsg}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group flex-1">
                <label className="form-label">Full Name</label>
                <div className="input-with-icon">
                  <User size={16} className="input-icon" />
                  <input
                    type="text"
                    name="name"
                    className="form-input"
                    placeholder="e.g. Jane Doe"
                    value={formData.name}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div className="form-group flex-1">
                <label className="form-label">Phone Number</label>
                <div className="input-with-icon">
                  <Phone size={16} className="input-icon" />
                  <input
                    type="tel"
                    name="phone"
                    className="form-input"
                    placeholder="+1 (555) 123-4567"
                    value={formData.phone}
                    onChange={handleChange}
                  />
                </div>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Email Address (Read-only)</label>
              <div className="input-with-icon">
                <Mail size={16} className="input-icon" />
                <input
                  type="email"
                  name="email"
                  className="form-input"
                  value={formData.email}
                  readOnly
                  disabled
                  style={{ opacity: 0.7 }}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Delivery / Office Address</label>
              <div className="input-with-icon" style={{ alignItems: 'flex-start' }}>
                <MapPin size={16} className="input-icon" style={{ top: '0.85rem' }} />
                <textarea
                  name="address"
                  rows="3"
                  className="form-input"
                  placeholder="Street, City, Postal Code, Country"
                  value={formData.address}
                  onChange={handleChange}
                ></textarea>
              </div>
            </div>

            <div className="mt-4" style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? (
                  'Saving Changes...'
                ) : (
                  <>
                    <Save size={16} /> Save Profile
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Profile;
