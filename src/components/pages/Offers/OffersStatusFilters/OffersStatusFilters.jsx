import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

export const OffersStatusFilters = ({ refreshOffers, statusFilters, updateStatusFilters }) => {
  const handleStatusFilterChange = useCallback(
    event => {
      updateStatusFilters(event.target.name, event.target.checked)
    },
    [updateStatusFilters]
  )

  return (
    <div className="offers-status-filters">
      <div className="osf-title">
        {'Afficher les statuts'}
      </div>
      <label>
        <input
          checked={statusFilters.active}
          name="active"
          onChange={handleStatusFilterChange}
          type="checkbox"
        />
        {'Active'}
      </label>
      <label>
        <input
          checked={statusFilters.inactive}
          name="inactive"
          onChange={handleStatusFilterChange}
          type="checkbox"
        />
        {'Inactive'}
      </label>
      <button
        className="primary-button"
        onClick={refreshOffers}
        type="button"
      >
        {'Appliquer'}
      </button>
    </div>
  )
}

OffersStatusFilters.propTypes = {
  refreshOffers: PropTypes.func.isRequired,
  statusFilters: PropTypes.shape({
    active: PropTypes.bool.isRequired,
    inactive: PropTypes.bool.isRequired,
  }).isRequired,
  updateStatusFilters: PropTypes.func.isRequired,
}
