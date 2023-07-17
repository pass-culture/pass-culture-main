import React from 'react'
import { useSelector } from 'react-redux'

import { SearchFiltersParams } from 'core/Offers/types'
import { Audience } from 'core/shared'
import { searchFiltersSelector } from 'store/offers/selectors'
import { BaseCheckbox } from 'ui-kit/form/shared'

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
  areAllOffersSelected,
  areOffersPresent,
  filters,
  isAdminForbidden,
  applyFilters,
  selectAllOffers,
  updateStatusFilter,
  audience,
  isAtLeastOneOfferChecked,
}: OffersTableHeadProps): JSX.Element => {
  const savedSearchFilters = useSelector(searchFiltersSelector)

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
