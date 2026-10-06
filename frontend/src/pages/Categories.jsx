import React, { useState, useEffect } from 'react';
import productService from '../services/productService';
import useAuth from '../hooks/useAuth';
import Loading from '../components/Loading';
import { Tags, Plus, Edit2, Trash2, X, AlertCircle } from 'lucide-react';

export const Categories = () => {
  const { isAdmin } = useAuth();
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const fetchCategories = async () => {
    try {
      setLoading(true);
      const data = await productService.getCategories();
      setCategories(data || []);
    } catch (err) {
      console.error('Failed to load categories', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCategories();
  }, []);

  const openCreateModal = () => {
    setEditingCategory(null);
    setFormData({ name: '', description: '' });
    setError('');
    setShowModal(true);
  };

  const openEditModal = (cat) => {
    setEditingCategory(cat);
    setFormData({ name: cat.name || '', description: cat.description || '' });
    setError('');
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingCategory(null);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      setError('Category name is required.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      if (editingCategory) {
        await productService.updateCategory(editingCategory.id, formData);
      } else {
        await productService.createCategory(formData);
      }
      closeModal();
      await fetchCategories();
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        'Error saving category.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this category?')) {
      try {
        await productService.deleteCategory(id);
        await fetchCategories();
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to delete category.');
      }
    }
  };

  if (loading) {
    return <Loading message="Loading product categories..." />;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Categories</h1>
          <p className="page-subtitle">Organize catalog items into distinct classifications</p>
        </div>
        {isAdmin && (
          <button className="btn btn-primary" onClick={openCreateModal}>
            <Plus size={16} /> Add Category
          </button>
        )}
      </div>

      <div className="card table-responsive">
        {categories.length === 0 ? (
          <div className="empty-state">
            <Tags size={40} className="empty-state-icon" />
            <h3>No Categories Defined</h3>
            <p>Group your products by creating standard inventory categories.</p>
            {isAdmin && (
              <button className="btn btn-primary mt-3" onClick={openCreateModal}>
                <Plus size={16} /> Add First Category
              </button>
            )}
          </div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Category Name</th>
                <th>Description</th>
                {isAdmin && <th>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {categories.map((cat) => (
                <tr key={cat.id}>
                  <td>
                    <span className="text-muted">#{cat.id}</span>
                  </td>
                  <td>
                    <div className="flex items-center gap-2">
                      <span className="category-pill-icon">🏷️</span>
                      <strong>{cat.name}</strong>
                    </div>
                  </td>
                  <td className="text-muted">{cat.description || 'No description'}</td>
                  {isAdmin && (
                    <td>
                      <div className="action-buttons-row">
                        <button
                          className="btn-icon-sm"
                          onClick={() => openEditModal(cat)}
                          title="Edit"
                        >
                          <Edit2 size={14} />
                        </button>
                        <button
                          className="btn-icon-sm btn-danger-ghost"
                          onClick={() => handleDelete(cat.id)}
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

      {/* Modal */}
      {showModal && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">
                {editingCategory ? 'Edit Category' : 'Create New Category'}
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
                  <label className="form-label">Category Name *</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Electronics, Perishables, Office Supplies"
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Description</label>
                  <textarea
                    rows="3"
                    className="form-input"
                    placeholder="Brief description of items under this category..."
                    value={formData.description}
                    onChange={(e) =>
                      setFormData({ ...formData, description: e.target.value })
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
                    : editingCategory
                    ? 'Update Category'
                    : 'Create Category'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Categories;
