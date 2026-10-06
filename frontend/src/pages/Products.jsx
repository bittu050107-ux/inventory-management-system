import React, { useState, useEffect } from 'react';
import productService from '../services/productService';
import inventoryService from '../services/inventoryService';
import useAuth from '../hooks/useAuth';
import ProductCard from '../components/ProductCard';
import Loading from '../components/Loading';
import { formatCurrency } from '../utils/helpers';
import {
  Package,
  Plus,
  Search,
  LayoutGrid,
  List,
  Edit2,
  Trash2,
  X,
  AlertCircle,
  Filter,
} from 'lucide-react';

export const Products = () => {
  const { isAdmin, isStaff } = useAuth();
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [suppliers, setSuppliers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' | 'table'

  // Modal States
  const [showModal, setShowModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [showStockModal, setShowStockModal] = useState(false);
  const [stockProduct, setStockProduct] = useState(null);
  const [stockType, setStockType] = useState('IN'); // 'IN' | 'OUT'
  const [stockQuantity, setStockQuantity] = useState(1);
  const [stockReason, setStockReason] = useState('');

  // Form State
  const [formData, setFormData] = useState({
    name: '',
    sku: '',
    description: '',
    price: '',
    category_id: '',
    supplier_id: '',
    reorder_level: 5,
  });
  const [formError, setFormError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [prods, cats, supps] = await Promise.all([
        productService.getProducts().catch(() => []),
        productService.getCategories().catch(() => []),
        productService.getSuppliers().catch(() => []),
      ]);
      setProducts(prods || []);
      setCategories(cats || []);
      setSuppliers(supps || []);
    } catch (err) {
      console.error('Failed to load products data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const openCreateModal = () => {
    setEditingProduct(null);
    setFormData({
      name: '',
      sku: `SKU-${Math.floor(1000 + Math.random() * 9000)}`,
      description: '',
      price: '',
      category_id: categories[0]?.id || '',
      supplier_id: suppliers[0]?.id || '',
      reorder_level: 5,
    });
    setFormError('');
    setShowModal(true);
  };

  const openEditModal = (product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name || '',
      sku: product.sku || '',
      description: product.description || '',
      price: product.price || '',
      category_id: product.category_id || '',
      supplier_id: product.supplier_id || '',
      reorder_level: product.reorder_level ?? 5,
    });
    setFormError('');
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingProduct(null);
    setFormError('');
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.sku || !formData.price) {
      setFormError('Please fill in Name, SKU, and Price.');
      return;
    }

    setIsSubmitting(true);
    setFormError('');

    try {
      const payload = {
        name: formData.name,
        sku: formData.sku,
        description: formData.description,
        price: parseFloat(formData.price),
        category_id: formData.category_id ? parseInt(formData.category_id) : null,
        supplier_id: formData.supplier_id ? parseInt(formData.supplier_id) : null,
        reorder_level: parseInt(formData.reorder_level) || 5,
      };

      if (editingProduct) {
        await productService.updateProduct(editingProduct.id, payload);
      } else {
        await productService.createProduct(payload);
      }

      closeModal();
      await fetchData();
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        'Error saving product.';
      setFormError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteProduct = async (id) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await productService.deleteProduct(id);
        await fetchData();
      } catch (err) {
        alert(err.response?.data?.detail || 'Failed to delete product.');
      }
    }
  };

  // Stock movement modal trigger
  const handleStockAction = (product, type) => {
    setStockProduct(product);
    setStockType(type);
    setStockQuantity(1);
    setStockReason(type === 'IN' ? 'Restock inventory' : 'Customer fulfillment');
    setShowStockModal(true);
  };

  const submitStockMovement = async (e) => {
    e.preventDefault();
    if (!stockProduct) return;

    try {
      setIsSubmitting(true);
      if (stockType === 'IN') {
        await inventoryService.stockIn({
          product_id: stockProduct.id,
          quantity: parseInt(stockQuantity),
          reason: stockReason,
        });
      } else {
        await inventoryService.stockOut({
          product_id: stockProduct.id,
          quantity: parseInt(stockQuantity),
          reason: stockReason,
        });
      }
      setShowStockModal(false);
      await fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || 'Stock movement failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Filtered products list
  const filteredProducts = products.filter((p) => {
    const matchesSearch =
      p.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.sku?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory =
      !selectedCategory || String(p.category_id) === String(selectedCategory);
    return matchesSearch && matchesCategory;
  });

  if (loading) {
    return <Loading message="Loading product catalog..." />;
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">Products Management</h1>
          <p className="page-subtitle">
            Manage your items, pricing, SKU codes, and inventory levels
          </p>
        </div>
        <div className="header-actions">
          {isAdmin && (
            <button className="btn btn-primary" onClick={openCreateModal}>
              <Plus size={16} /> Add Product
            </button>
          )}
        </div>
      </div>

      {/* Filter and View Controls Bar */}
      <div className="filter-bar">
        <div className="search-input-box">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            className="form-input search-input"
            placeholder="Search by product name or SKU..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-select-box">
          <Filter size={16} className="select-icon" />
          <select
            className="form-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div className="view-toggle-group">
          <button
            className={`btn-icon ${viewMode === 'grid' ? 'active' : ''}`}
            onClick={() => setViewMode('grid')}
            title="Grid View"
          >
            <LayoutGrid size={18} />
          </button>
          <button
            className={`btn-icon ${viewMode === 'table' ? 'active' : ''}`}
            onClick={() => setViewMode('table')}
            title="Table View"
          >
            <List size={18} />
          </button>
        </div>
      </div>

      {/* Content Area */}
      {filteredProducts.length === 0 ? (
        <div className="empty-state card">
          <Package size={48} className="empty-state-icon" />
          <h3>No Products Found</h3>
          <p>Try refining your search terms or add a new product to get started.</p>
          {isAdmin && (
            <button className="btn btn-primary mt-3" onClick={openCreateModal}>
              <Plus size={16} /> Create First Product
            </button>
          )}
        </div>
      ) : viewMode === 'grid' ? (
        <div className="products-grid">
          {filteredProducts.map((p) => (
            <ProductCard
              key={p.id}
              product={p}
              canManage={isAdmin}
              onEdit={openEditModal}
              onDelete={handleDeleteProduct}
              onStockAction={isStaff ? handleStockAction : null}
            />
          ))}
        </div>
      ) : (
        <div className="card table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>SKU</th>
                <th>Name</th>
                <th>Category</th>
                <th>Price</th>
                <th>Stock</th>
                <th>Reorder Level</th>
                {isAdmin && <th>Actions</th>}
              </tr>
            </thead>
            <tbody>
              {filteredProducts.map((p) => (
                <tr key={p.id}>
                  <td>
                    <code className="text-mono">{p.sku}</code>
                  </td>
                  <td>
                    <strong>{p.name}</strong>
                  </td>
                  <td>
                    <span className="badge badge-neutral">
                      {categories.find((c) => c.id === p.category_id)?.name || 'General'}
                    </span>
                  </td>
                  <td>{formatCurrency(p.price)}</td>
                  <td>
                    <span
                      className={`font-semibold ${
                        (p.stock_quantity ?? p.stock ?? 0) <= (p.reorder_level || 5)
                          ? 'text-danger'
                          : 'text-success'
                      }`}
                    >
                      {p.stock_quantity ?? p.stock ?? 0}
                    </span>
                  </td>
                  <td>{p.reorder_level || 5}</td>
                  {isAdmin && (
                    <td>
                      <div className="action-buttons-row">
                        <button
                          className="btn-icon-sm"
                          onClick={() => openEditModal(p)}
                          title="Edit"
                        >
                          <Edit2 size={14} />
                        </button>
                        <button
                          className="btn-icon-sm btn-danger-ghost"
                          onClick={() => handleDeleteProduct(p.id)}
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
        </div>
      )}

      {/* Add / Edit Product Modal */}
      {showModal && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">
                {editingProduct ? 'Edit Product' : 'Add New Product'}
              </h2>
              <button className="btn-icon" onClick={closeModal}>
                <X size={18} />
              </button>
            </div>

            {formError && (
              <div className="alert alert-error">
                <AlertCircle size={16} />
                <span>{formError}</span>
              </div>
            )}

            <form onSubmit={handleFormSubmit}>
              <div className="modal-body">
                <div className="form-row">
                  <div className="form-group flex-1">
                    <label className="form-label">Product Name *</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g. Wireless Mouse"
                      value={formData.name}
                      onChange={(e) =>
                        setFormData({ ...formData, name: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div className="form-group flex-1">
                    <label className="form-label">SKU Code *</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g. SKU-1001"
                      value={formData.sku}
                      onChange={(e) =>
                        setFormData({ ...formData, sku: e.target.value })
                      }
                      required
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group flex-1">
                    <label className="form-label">Unit Price ($) *</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      className="form-input"
                      placeholder="29.99"
                      value={formData.price}
                      onChange={(e) =>
                        setFormData({ ...formData, price: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div className="form-group flex-1">
                    <label className="form-label">Reorder Level Threshold</label>
                    <input
                      type="number"
                      min="0"
                      className="form-input"
                      value={formData.reorder_level}
                      onChange={(e) =>
                        setFormData({ ...formData, reorder_level: e.target.value })
                      }
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group flex-1">
                    <label className="form-label">Category</label>
                    <select
                      className="form-select"
                      value={formData.category_id}
                      onChange={(e) =>
                        setFormData({ ...formData, category_id: e.target.value })
                      }
                    >
                      <option value="">Select Category</option>
                      {categories.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group flex-1">
                    <label className="form-label">Supplier</label>
                    <select
                      className="form-select"
                      value={formData.supplier_id}
                      onChange={(e) =>
                        setFormData({ ...formData, supplier_id: e.target.value })
                      }
                    >
                      <option value="">Select Supplier</option>
                      {suppliers.map((s) => (
                        <option key={s.id} value={s.id}>
                          {s.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Description</label>
                  <textarea
                    rows="3"
                    className="form-input"
                    placeholder="Technical specifications, features, or storage guidelines..."
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
                  disabled={isSubmitting}
                >
                  {isSubmitting
                    ? 'Saving...'
                    : editingProduct
                    ? 'Update Product'
                    : 'Create Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Stock In / Out Modal */}
      {showStockModal && stockProduct && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <div className="modal-header">
              <h2 className="modal-title">
                {stockType === 'IN' ? 'Stock In (Restock)' : 'Stock Out (Fulfill)'}
              </h2>
              <button
                className="btn-icon"
                onClick={() => setShowStockModal(false)}
              >
                <X size={18} />
              </button>
            </div>
            <form onSubmit={submitStockMovement}>
              <div className="modal-body">
                <p className="mb-2">
                  Product: <strong>{stockProduct.name}</strong> ({stockProduct.sku})
                </p>
                <div className="form-group">
                  <label className="form-label">Quantity</label>
                  <input
                    type="number"
                    min="1"
                    className="form-input"
                    value={stockQuantity}
                    onChange={(e) => setStockQuantity(e.target.value)}
                    required
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Reason / Notes</label>
                  <input
                    type="text"
                    className="form-input"
                    placeholder="e.g. Purchase order PO-9923"
                    value={stockReason}
                    onChange={(e) => setStockReason(e.target.value)}
                    required
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowStockModal(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className={`btn ${
                    stockType === 'IN' ? 'btn-success' : 'btn-warning'
                  }`}
                  disabled={isSubmitting}
                >
                  {isSubmitting
                    ? 'Processing...'
                    : `Confirm Stock ${stockType === 'IN' ? 'In' : 'Out'}`}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Products;
