import React from 'react'

import { FilterField, Option } from 'app/types'
import { Tag } from 'app/ui-kit'
import { ReactComponent as ResetIcon } from 'assets/reset.svg'
import { VenueFilterType } from 'utils/types'

import './OfferFiltersTags.scss'

export const OfferFiltersTags = ({
  venueFilter,
  removeVenueFilter,
  departments,
  handleRemoveFilter,
  handleResetFilters,
  students,
  categories,
}: {
  venueFilter: VenueFilterType | null
  removeVenueFilter: () => void
  departments: Option[]
  handleRemoveFilter: (
    filterValue: string | string[],
    filter: FilterField
  ) => void
  handleResetFilters: () => void
  students: Option[]
  categories: Option<string[]>[]
}): JSX.Element => {
  const hasActiveFilters = Boolean(
    venueFilter?.id ||
      departments.length > 0 ||
      students.length > 0 ||
      categories.length > 0
  )

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
            onClick={() =>
              handleRemoveFilter(department.value, FilterField.DEPARTMENTS)
            }
          />
        ))}
        {categories.map(category => (
          <Tag
            key={category.value.join(',')}
            label={category.label}
            onClick={() =>
              handleRemoveFilter(category.value, FilterField.CATEGORIES)
            }
          />
        ))}
        {students.map(student => (
          <Tag
            key={student.value}
            label={student.label}
            onClick={() =>
              handleRemoveFilter(student.value, FilterField.STUDENTS)
            }
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
