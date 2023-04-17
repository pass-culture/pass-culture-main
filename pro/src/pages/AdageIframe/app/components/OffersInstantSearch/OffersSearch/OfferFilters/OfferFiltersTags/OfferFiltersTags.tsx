import React, { useContext } from 'react'

import { VenueResponse } from 'apiClient/adage'
import './OfferFiltersTags.scss'
import { ReactComponent as ResetIcon } from 'icons/reset.svg'
import {
  AlgoliaQueryContext,
  FiltersContext,
} from 'pages/AdageIframe/app/providers'
import { Option } from 'pages/AdageIframe/app/types'
import { Tag } from 'ui-kit'

export const OfferFiltersTags = ({
  venueFilter,
  removeVenueFilter,
  handleResetFilters,
}: {
  venueFilter: VenueResponse | null
  removeVenueFilter: () => void
  handleResetFilters: () => void
}): JSX.Element => {
  const {
    currentFilters: { categories, students, departments, domains },
    dispatchCurrentFilters,
  } = useContext(FiltersContext)
  const { queryTag, removeQuery } = useContext(AlgoliaQueryContext)

  const hasActiveFilters = Boolean(
    queryTag ||
      venueFilter?.id ||
      departments.length > 0 ||
      students.length > 0 ||
      categories.length > 0 ||
      domains.length > 0
  )

  const handleRemoveDepartmentFilter = (
    departmentToBeRemoved: Option
  ): void => {
    dispatchCurrentFilters({
      type: 'REMOVE_ONE_DEPARTMENT_FILTER',
      departmentFilter: departmentToBeRemoved,
    })
  }

  const handleRemoveCategoriesFilter = (
    categoryToBeRemoved: Option<string[]>
  ): void => {
    dispatchCurrentFilters({
      type: 'REMOVE_ONE_CATEGORY_FILTER',
      categoryFilter: categoryToBeRemoved,
    })
  }

  const handleRemoveDomainsFilter = (
    domainToBeRemoved: Option<number>
  ): void => {
    dispatchCurrentFilters({
      type: 'REMOVE_ONE_DOMAIN_FILTER',
      domainFilter: domainToBeRemoved,
    })
  }

  const handleRemoveStudentsFilter = (studentToBeRemoved: Option): void => {
    dispatchCurrentFilters({
      type: 'REMOVE_ONE_STUDENT_FILTER',
      studentFilter: studentToBeRemoved,
    })
  }

  const handleRemoveQueryFilter = (): void => {
    removeQuery()
  }

  return (
    <div className="offer-filters-tags-container">
      <div className="offer-filters-tags">
        {queryTag ? (
          <Tag
            label={queryTag}
            closeable={{ onClose: handleRemoveQueryFilter }}
          />
        ) : null}
        {venueFilter?.id ? (
          <Tag
            key={venueFilter.id}
            label={`Lieu : ${venueFilter.publicName || venueFilter.name}`}
            closeable={{ onClose: removeVenueFilter }}
          />
        ) : null}
        {departments.map(department => (
          <Tag
            key={department.value}
            label={department.label}
            closeable={{
              onClose: () => handleRemoveDepartmentFilter(department),
            }}
          />
        ))}
        {categories.map(category => (
          <Tag
            key={category.value.join(',')}
            label={category.label}
            closeable={{
              onClose: () => handleRemoveCategoriesFilter(category),
            }}
          />
        ))}
        {domains.map(domain => (
          <Tag
            key={domain.value}
            label={domain.label}
            closeable={{ onClose: () => handleRemoveDomainsFilter(domain) }}
          />
        ))}
        {students.map(student => (
          <Tag
            key={student.value}
            label={student.label}
            closeable={{ onClose: () => handleRemoveStudentsFilter(student) }}
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
