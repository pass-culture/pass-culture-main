import React from 'react'

import { SearchFiltersParams } from 'core/Offers/types'
import { Audience } from 'core/shared/types'

import { StatusFiltersButton } from './StatusFiltersButton'

type OffersTableHeadProps = {
  applyFilters: () => void
  areAllOffersSelected: boolean
  areOffersPresent: boolean
  filters: SearchFiltersParams
  isAdminForbidden: (searchFilters: SearchFiltersParams) => boolean
  updateStatusFilter: (status: SearchFiltersParams['status']) => void
  audience: Audience
  isAtLeastOneOfferChecked: boolean
}

export const OffersTableHead = ({
  filters,
  isAdminForbidden,
  applyFilters,
  updateStatusFilter,
  audience,
}: OffersTableHeadProps): JSX.Element => {
  return (
    <thead>
      <tr>
        <th colSpan={3} />

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
