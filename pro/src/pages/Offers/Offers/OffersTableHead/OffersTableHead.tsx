import React from 'react'

import { ALL_STATUS } from 'core/Offers/constants'
import { SearchFiltersParams } from 'core/Offers/types'
import { Audience } from 'core/shared'

import StatusFiltersButton from './StatusFiltersButton'

type OffersTableHeadProps = {
  applyFilters: () => void
  areAllOffersSelected: boolean
  areOffersPresent: boolean
  filters?: SearchFiltersParams
  isAdminForbidden: (searchFilters: SearchFiltersParams) => boolean
  selectAllOffers: () => void
  updateStatusFilter: (status: SearchFiltersParams['status']) => void
  audience: Audience
  isAtLeastOneOfferChecked: boolean
}

const OffersTableHead = ({
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
            disabled={false}
            status={ALL_STATUS}
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
