/**
 * Helper utility functions for formatting and calculations
 */

export const formatCurrency = (amount) => {
  const num = Number(amount) || 0;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(num);
};

export const formatDate = (dateString) => {
  if (!dateString) return '—';
  try {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  } catch {
    return dateString;
  }
};

export const getStatusBadgeClass = (status) => {
  switch ((status || '').toUpperCase()) {
    case 'CONFIRMED':
    case 'IN_STOCK':
    case 'COMPLETED':
      return 'badge-success';
    case 'PENDING':
    case 'PROCESSING':
      return 'badge-warning';
    case 'SHIPPED':
      return 'badge-info';
    case 'DELIVERED':
      return 'badge-primary';
    case 'CANCELLED':
    case 'OUT_OF_STOCK':
      return 'badge-danger';
    case 'LOW_STOCK':
      return 'badge-amber';
    default:
      return 'badge-neutral';
  }
};

export const getRoleBadgeClass = (role) => {
  switch ((role || '').toUpperCase()) {
    case 'ADMIN':
      return 'badge-purple';
    case 'MANAGER':
      return 'badge-indigo';
    case 'STAFF':
      return 'badge-blue';
    default:
      return 'badge-neutral';
  }
};
