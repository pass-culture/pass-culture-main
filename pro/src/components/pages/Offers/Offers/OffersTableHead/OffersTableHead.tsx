import { ADMINS_DISABLED_FILTERS_MESSAGE } from 'core/Offers/constants'
import { Audience } from 'core/shared'
import React from 'react'
import StatusFiltersButton from './StatusFiltersButton'
import { TSearchFilters } from 'core/Offers/types'
import { searchFiltersSelector } from 'store/offers/selectors'
import useActiveFeature from 'components/hooks/useActiveFeature'
import { useSelector } from 'react-redux'

type OffersTableHeadProps = {
  applyFilters: () => void
  areAllOffersSelected: boolean
  areOffersPresent: boolean
  filters: TSearchFilters
  isAdminForbidden: (searchFilters: TSearchFilters) => boolean
  selectAllOffers: () => void
  updateStatusFilter: (status: string) => void
  audience: Audience
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
}: OffersTableHeadProps): JSX.Element => {
  const savedSearchFilters = useSelector(searchFiltersSelector)
  const enableEducationalInstitutionAssociation = useActiveFeature(
    'ENABLE_EDUCATIONAL_INSTITUTION_ASSOCIATION'
  )

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
        {audience === Audience.INDIVIDUAL && <th />}
        <th>Lieu</th>
        <th>
          {audience === Audience.COLLECTIVE &&
          enableEducationalInstitutionAssociation
            ? 'Etablissement'
            : 'Stocks'}
        </th>
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

export default OffersTableHead
