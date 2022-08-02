import React, { useContext, useEffect, useState } from 'react'

import { VenueResponse } from 'api/gen'
import { getEducationalCategoriesOptionsAdapter } from 'app/adapters/getEducationalCategoriesOptionsAdapter'
import { getEducationalDomainsOptionsAdapter } from 'app/adapters/getEducationalDomainsOptionsAdapter'
import { departmentOptions } from 'app/constants/departmentOptions'
import { AlgoliaQueryContext } from 'app/providers'
import { FiltersContext } from 'app/providers/FiltersContextProvider'
import { Filters, Option } from 'app/types'
import { Button, MultiSelectAutocomplete } from 'app/ui-kit'

import OfferFiltersTags from './OfferFiltersTags'
import './OfferFilters.scss'
import { studentsOptions } from './studentsOptions'

export interface OfferFiltersProps {
  className?: string
  handleLaunchSearchButton: (filters: Filters) => void
  venueFilter: VenueResponse | null
  removeVenueFilter: () => void
  isLoading: boolean
}

export const OfferFilters = ({
  className,
  handleLaunchSearchButton,
  venueFilter,
  removeVenueFilter,
  isLoading,
}: OfferFiltersProps): JSX.Element => {
  const [categoriesOptions, setCategoriesOptions] = useState<
    Option<string[]>[]
  >([])
  const [domainsOptions, setDomainsOptions] = useState<Option<number>[]>([])
  const { dispatchCurrentFilters, currentFilters } = useContext(FiltersContext)
  const { removeQuery } = useContext(AlgoliaQueryContext)

  const handleResetFilters = () => {
    removeVenueFilter()
    removeQuery()
    dispatchCurrentFilters({
      type: 'RESET_CURRENT_FILTERS',
    })
  }

  useEffect(() => {
    const loadFiltersOptions = async () => {
      const [categoriesResponse, domainsResponse] = await Promise.all([
        getEducationalCategoriesOptionsAdapter(null),
        getEducationalDomainsOptionsAdapter(),
      ])

      if (categoriesResponse.isOk) {
        setCategoriesOptions(categoriesResponse.payload.educationalCategories)
      }

      if (domainsResponse.isOk) {
        setDomainsOptions(domainsResponse.payload)
      }
    }

    loadFiltersOptions()
  }, [])

  return (
    <div className={className}>
      <span className="offer-filters-title">Filtrer par :</span>
      <div className="offer-filters-row">
        <MultiSelectAutocomplete
          className="offer-filters-filter"
          initialValues={currentFilters.departments}
          label="Département"
          onChange={departments =>
            dispatchCurrentFilters({
              type: 'POPULATE_DEPARTMENTS_FILTER',
              departmentFilters: departments,
            })
          }
          options={departmentOptions}
          pluralLabel="Départements"
        />
        <MultiSelectAutocomplete
          className="offer-filters-filter"
          initialValues={currentFilters.categories}
          label="Catégorie"
          onChange={categories =>
            dispatchCurrentFilters({
              type: 'POPULATE_CATEGORIES_FILTER',
              categoryFilters: categories,
            })
          }
          options={categoriesOptions}
          pluralLabel="Catégories"
        />
        <MultiSelectAutocomplete<number>
          className="offer-filters-filter"
          initialValues={currentFilters.domains}
          label="Domaine"
          onChange={domains =>
            dispatchCurrentFilters({
              type: 'POPULATE_DOMAINS_FILTER',
              domainFilters: domains,
            })
          }
          options={domainsOptions}
          pluralLabel="Domaines"
        />
        <MultiSelectAutocomplete
          className="offer-filters-filter"
          initialValues={currentFilters.students}
          label="Niveau scolaire"
          onChange={students =>
            dispatchCurrentFilters({
              type: 'POPULATE_STUDENTS_FILTER',
              studentFilters: students,
            })
          }
          options={studentsOptions}
          pluralLabel="Niveaux scolaires"
        />
      </div>
      <OfferFiltersTags
        handleResetFilters={handleResetFilters}
        removeVenueFilter={removeVenueFilter}
        venueFilter={venueFilter}
      />
      <div className="offer-filters-button-container">
        <div className="offer-filters-button-separator" />
        <Button
          disabled={isLoading}
          label="Lancer la recherche"
          onClick={() => {
            handleLaunchSearchButton(currentFilters)
          }}
        />
      </div>
    </div>
  )
}
