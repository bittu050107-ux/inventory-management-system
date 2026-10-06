import React, { useState, useEffect } from 'react';
import productService from '../services/productService';
import useAuth from '../hooks/useAuth';
import Loading from '../components/Loading';
import { Truck, Plus, Edit2, Trash2, X, AlertCircle, Mail, Phone, MapPin } from 'lucide-react';

export const Suppliers = () => {
  const { isAdmin } = useAuth();
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingSupplier, setEditingSupplier] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    contact_name: '',
    email: '',
    phone: '',
    address: '',
  });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchSuppliers = async () => {
    try {
      setLoading(true);
      const data = await productService.getSuppliers();
      setSuppliers(data || []);
    } catch (err) {
      console.error('Failed to load suppliers', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSuppliers();
  }, []);

  const openCreateModal = () => {
    setEditingSupplier(null);
    setFormData({
      name: '',
      contact_name: '',
      email: '',
      phone: '',
      address: '',
    });
    setError('');
    setShowModal(true);
  };

  const openEditModal = (sup) => {
    setEditingSupplier(sup);
    setFormData({
      name: sup.name || '',
      contact_name: sup.contact_name || '',
      email: sup.email || '',
      phone: sup.phone || '',
      address: sup.address || '',
    });
    setError('');
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingSupplier(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      setError('Supplier company name is required.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      if (editingSupplier) {
        await productService.updateSupplier(editingSupplier.id, formData);
      } else {
        await productService.createSupplier(formData);
      }
      closeModal();
      await fetchSuppliers();
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        'Error saving supplier.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this supplier?')) {
      try {
        await productService.deleteSupplier(id);
        await fetchSuppliers();
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to delete supplier.');
      }
    }
  };

  if (loading) {
    return <Loading message="Loading suppliers directory..." />;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Suppliers</h1>
          <p className="page-subtitle">Manage vendors, procurement channels, and contact points</p>
        </div>
        {isAdmin && (
          <button className="btn btn-primary" onClick={openCreateModal}>
            <Plus size={16} /> Add Supplier
          </button>
        )}
      </div>

      <div className="card table-responsive">
        {suppliers.length === 0 ? (
          <div className="empty-state">
            <Truck size={40} className="empty-state-icon" />
            <h3>No Suppliers Listed</h3>
            <p>Maintain your vendor relationships by adding suppliers.</p>
            {isAdmin && (
              <button className="btn btn-primary mt-3" onClick={openCreateModal}>
                <Plus size={16} /> Add First Supplier
              </button>
            )}
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Contact Person</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Address</th>
                {isAdmin && <th>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {suppliers.map((sup) => (
                <tr key={sup.id}>
                  <td>
                    <strong>{sup.name}</strong>
                  </td>
                  <td>{sup.contact_name || '—'}</td>
                  <td>
                    {sup.email ? (
                      <span className="flex items-center gap-1 text-sm">
                        <Mail size={12} className="text-muted" /> {sup.email}
                      </span>
                    ) : (
                      '—'
                    )}
                  </td>
                  <td>
                    {sup.phone ? (
                      <span className="flex items-center gap-1 text-sm">
                        <Phone size={12} className="text-muted" /> {sup.phone}
                      </span>
                    ) : (
                      '—'
                    )}
                  </td>
                  <td>
                    {sup.address ? (
                      <span className="flex items-center gap-1 text-sm text-muted">
                        <MapPin size={12} /> {sup.address}
                      </span>
                    ) : (
                      '—'
                    )}
                  </td>
                  {isAdmin && (
                    <td>
                      <div className="action-buttons-row">
                        <button
                          className="btn-icon-sm"
                          onClick={() => openEditModal(sup)}
                          title="Edit"
                        >
                          <Edit2 size={14} />
                        </button>
                        <button
                          className="btn-icon-sm btn-danger-ghost"
                          onClick={() => handleDelete(sup.id)}
                          title="Delete"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Supplier Modal */}
      {showModal && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">
                {editingSupplier ? 'Edit Supplier' : 'Add New Supplier'}
              </h2>
              <button className="btn-icon" onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            {error && (
              <div className="alert alert-error">
                <AlertCircle size={16} />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit}>
              <div className="modal-body">
                <div className="form-group">
                  <label className="form-label">Supplier Company Name *</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Acme Logistics Global"
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    required
                  />
                </div>

                <div className="form-row">
                  <div className="form-group flex-1">
                    <label className="form-label">Contact Person</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g. John Doe"
                      value={formData.contact_name}
                      onChange={(e) =>
                        setFormData({ ...formData, contact_name: e.target.value })
                      }
                    />
                  </div>
                  <div className="form-group flex-1">
                    <label className="form-label">Phone Number</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="+1 (555) 000-0000"
                      value={formData.phone}
                      onChange={(e) =>
                        setFormData({ ...formData, phone: e.target.value })
                      }
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Email Address</label>
                  <input
                    type="email"
                    className="form-input"
                    placeholder="sales@acme.com"
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({ ...formData, email: e.target.value })
                    }
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Physical Address</label>
                  <textarea
                    rows="2"
                    className="form-input"
                    placeholder="Warehouse location, city, country..."
                    value={formData.address}
                    onChange={(e) =>
                      setFormData({ ...formData, address: e.target.value })
                    }
                  ></textarea>
                </div>
              </div>

              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={closeModal}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={submitting}
                >
                  {submitting
                    ? 'Saving...'
                    : editingSupplier
                    ? 'Update Supplier'
                    : 'Create Supplier'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Suppliers;
