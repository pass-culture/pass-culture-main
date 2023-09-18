import React from 'react'

import { SearchFiltersParams } from 'core/Offers/types'
import { Audience } from 'core/shared'

import StatusFiltersButton from './StatusFiltersButton'

type OffersTableHeadProps = {
  applyFilters: () => void
  areAllOffersSelected: boolean
  areOffersPresent: boolean
  filters: SearchFiltersParams
  isAdminForbidden: (searchFilters: SearchFiltersParams) => boolean
  selectAllOffers: () => void
  updateStatusFilter: (status: SearchFiltersParams['status']) => void
  audience: Audience
  isAtLeastOneOfferChecked: boolean
}

const OffersTableHead = ({
  filters,
  isAdminForbidden,
  applyFilters,
  updateStatusFilter,
  audience,
}: OffersTableHeadProps): JSX.Element => {
  return (
    <thead>
      <tr>
        <th
          className={`th-checkbox ${
            isAdminForbidden(savedSearchFilters) || !areOffersPresent
              ? 'label-disabled'
              : ''
          }`}
          colSpan={3}
        >
          <BaseCheckbox
            checked={areAllOffersSelected || isAtLeastOneOfferChecked}
            partialCheck={!areAllOffersSelected && isAtLeastOneOfferChecked}
            disabled={isAdminForbidden(savedSearchFilters) || !areOffersPresent}
            onChange={selectAllOffers}
            label="Tout sélectionner"
          />
        </th>

        <th>Lieu</th>
        <th>{audience === Audience.COLLECTIVE ? 'Établissement' : 'Stocks'}</th>
        <th className="th-with-filter">
          <StatusFiltersButton
            applyFilters={applyFilters}
            disabled={isAdminForbidden(filters)}
            status={filters.status}
            updateStatusFilter={updateStatusFilter}
            audience={audience}
          />
        </th>
        <th className="th-actions">Actions</th>
      </tr>
    </thead>
  )
}

export default OffersTableHead
