import { ADMINS_DISABLED_FILTERS_MESSAGE } from 'core/Offers/constants'
import PropTypes from 'prop-types'
import React from 'react'
import StatusFiltersButton from './StatusFiltersButton'
import { useSelector } from 'react-redux'

const OffersTableHead = ({
  areAllOffersSelected,
  areOffersPresent,
  filters,
  isAdminForbidden,
  applyFilters,
  selectAllOffers,
  updateStatusFilter,
}) => {
  const savedSearchFilters = useSelector(state => state.offers.searchFilters)

  return (
    <thead>
      <tr>
        <th className="th-checkbox">
          <input
            checked={areAllOffersSelected}
            className="select-offer-checkbox"
            disabled={isAdminForbidden(savedSearchFilters) || !areOffersPresent}
            id="select-offer-checkbox"
            onChange={selectAllOffers}
            type="checkbox"
          />
        </th>
        <th
          className={`th-checkbox-label ${
            isAdminForbidden(savedSearchFilters) || !areOffersPresent
              ? 'label-disabled'
              : ''
          }`}
        >
          <label
            htmlFor="select-offer-checkbox"
            title={
              isAdminForbidden(savedSearchFilters)
                ? ADMINS_DISABLED_FILTERS_MESSAGE
                : undefined
            }
          >
            {areAllOffersSelected ? 'Tout désélectionner' : 'Tout sélectionner'}
          </label>
        </th>
        <th />
        <th>Lieu</th>
        <th>Stock</th>
        <th className="th-with-filter">
          <StatusFiltersButton
            applyFilters={applyFilters}
            disabled={isAdminForbidden(filters)}
            status={filters.status}
            updateStatusFilter={updateStatusFilter}
          />
        </th>
        <th />
        <th />
      </tr>
    </thead>
  )
}

OffersTableHead.propTypes = {
  applyFilters: PropTypes.func.isRequired,
  areAllOffersSelected: PropTypes.bool.isRequired,
  areOffersPresent: PropTypes.bool.isRequired,
  filters: PropTypes.shape({
    status: PropTypes.string,
  }).isRequired,
  isAdminForbidden: PropTypes.func.isRequired,
  selectAllOffers: PropTypes.func.isRequired,
  updateStatusFilter: PropTypes.func.isRequired,
}

export default OffersTableHead
