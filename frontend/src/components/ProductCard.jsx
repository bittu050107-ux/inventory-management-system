import React from 'react';
import { formatCurrency, getStatusBadgeClass } from '../utils/helpers';
import { Edit2, Trash2, ArrowUpRight, ArrowDownRight, Tag } from 'lucide-react';

export const ProductCard = ({
  product,
  onEdit,
  onDelete,
  onStockAction,
  canManage = false,
}) => {
  const stock = product.stock_quantity ?? product.stock ?? 0;
  const isLowStock = stock <= (product.reorder_level || 5);
  const isOutOfStock = stock <= 0;

  const stockStatus = isOutOfStock
    ? 'OUT_OF_STOCK'
    : isLowStock
    ? 'LOW_STOCK'
    : 'IN_STOCK';

  const stockStatusLabel = isOutOfStock
    ? 'Out of Stock'
    : isLowStock
    ? `Low Stock (${stock})`
    : `In Stock (${stock})`;

  return (
    <div className="product-card">
      <div className="product-card-header">
        <div className="product-sku">
          <Tag size={12} />
          <span>{product.sku || 'NO-SKU'}</span>
        </div>
        <span className={`badge ${getStatusBadgeClass(stockStatus)}`}>
          {stockStatusLabel}
        </span>
      </div>

      <div className="product-card-body">
        <h3 className="product-name" title={product.name}>
          {product.name}
        </h3>
        <p className="product-description">
          {product.description || 'No description provided.'}
        </p>

        <div className="product-meta-row">
          <div className="product-category">
            <span className="meta-label">Category</span>
            <span className="meta-value">{product.category_name || product.category || 'General'}</span>
          </div>
          <div className="product-price-box">
            <span className="meta-label">Price</span>
            <span className="product-price">{formatCurrency(product.price)}</span>
          </div>
        </div>
      </div>

      <div className="product-card-footer">
        <div className="product-quick-actions">
          {onStockAction && (
            <>
              <button
                className="btn-sm btn-outline-success"
                onClick={() => onStockAction(product, 'IN')}
                title="Stock In"
              >
                <ArrowDownRight size={14} /> In
              </button>
              <button
                className="btn-sm btn-outline-warning"
                onClick={() => onStockAction(product, 'OUT')}
                title="Stock Out"
                disabled={isOutOfStock}
              >
                <ArrowUpRight size={14} /> Out
              </button>
            </>
          )}
        </div>

        {canManage && (
          <div className="product-admin-actions">
            {onEdit && (
              <button
                className="btn-icon-sm"
                onClick={() => onEdit(product)}
                title="Edit Product"
              >
                <Edit2 size={15} />
              </button>
            )}
            {onDelete && (
              <button
                className="btn-icon-sm btn-danger-ghost"
                onClick={() => onDelete(product.id)}
                title="Delete Product"
              >
                <Trash2 size={15} />
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductCard;
