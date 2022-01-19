import React from 'react'

import { Option } from 'app/types'
import { Tag } from 'app/ui-kit'
import { ReactComponent as ResetIcon } from 'assets/reset.svg'
import { VenueFilterType } from 'utils/types'

import './OfferFiltersTags.scss'

export const OfferFiltersTags = ({
  venueFilter,
  removeVenueFilter,
  departments,
  handleDeleteFilter,
  handleResetFilters,
  students,
}: {
  venueFilter: VenueFilterType | null
  removeVenueFilter: () => void
  departments: Option[]
  handleDeleteFilter: (filterValue: string) => void
  handleResetFilters: () => void
  students: Option[]
}): JSX.Element => {
  const hasActiveFilters = Boolean(venueFilter?.id || departments.length > 0)

  return (
    <div className="offer-filters-tags-container">
      <div className="offer-filters-tags">
        {venueFilter?.id ? (
          <Tag
            key={venueFilter.id}
            label={`Lieu : ${venueFilter.publicName || venueFilter.name}`}
            onClick={removeVenueFilter}
          />
        ) : null}
        {departments.map(department => (
          <Tag
            key={department.value}
            label={department.label}
            onClick={() => handleDeleteFilter(department.value)}
          />
        ))}
        {students.map(department => (
          <Tag
            key={department.value}
            label={department.label}
            onClick={() => handleDeleteFilter(department.value)}
          />
        ))}
      </div>
      {hasActiveFilters && (
        <button
          className="offer-filters-reset"
          onClick={handleResetFilters}
          type="button"
        >
          <ResetIcon className="offer-filters-reset-icon" />
          Réinitialiser les filtres
        </button>
      )}
    </div>
  )
}

export default OfferFiltersTags
