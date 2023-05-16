import React, { useCallback, useContext, useEffect, useState } from 'react'

import {
  AdageFrontRoles,
  AuthenticatedResponse,
  VenueResponse,
} from 'apiClient/adage'
import './OfferFilters.scss'
import { getEducationalCategoriesOptionsAdapter } from 'pages/AdageIframe/app/adapters/getEducationalCategoriesOptionsAdapter'
import { getEducationalDomainsOptionsAdapter } from 'pages/AdageIframe/app/adapters/getEducationalDomainsOptionsAdapter'
import { departmentOptions } from 'pages/AdageIframe/app/constants/departmentOptions'
import {
  AlgoliaQueryContext,
  FiltersContext,
} from 'pages/AdageIframe/app/providers'
import { Option, Filters } from 'pages/AdageIframe/app/types'
import { MultiSelectAutocomplete } from 'pages/AdageIframe/app/ui-kit'
import { Button } from 'ui-kit'
import { BaseCheckbox } from 'ui-kit/form/shared'

import OfferFiltersTags from './OfferFiltersTags'
import { studentsOptions } from './studentsOptions'

interface OfferFiltersProps {
  className?: string
  handleLaunchSearchButton: (filters: Filters) => void
  venueFilter: VenueResponse | null
  removeVenueFilter: () => void
  isLoading: boolean
  user: AuthenticatedResponse
}

const getOnlyInMyDptLabel = (user: AuthenticatedResponse) => {
  const userInformation =
    user.institutionCity &&
    user.departmentCode &&
    `${user.institutionCity} (${user.departmentCode})`

  if (!userInformation) {
    return ''
  }

  return (
    <span>
      Les acteurs culturels de mon département : <b>{userInformation}</b>
    </span>
  )
}

const getOnlyInMySchoolLabel = (user: AuthenticatedResponse) => {
  const userInformation =
    user.institutionName &&
    user.institutionCity &&
    user.departmentCode &&
    `${user.institutionName} - ${user.institutionCity} (${user.departmentCode})`

  if (!userInformation) {
    return ''
  }

  return (
    <span>
      Les acteurs qui se déplacent dans mon établissement :{' '}
      <b>{userInformation}</b>
    </span>
  )
}

export const OfferFilters = ({
  className,
  handleLaunchSearchButton,
  venueFilter,
  removeVenueFilter,
  isLoading,
  user,
}: OfferFiltersProps): JSX.Element => {
  const [categoriesOptions, setCategoriesOptions] = useState<
    Option<string[]>[]
  >([])
  const [domainsOptions, setDomainsOptions] = useState<Option<number>[]>([])

  const { dispatchCurrentFilters, currentFilters } = useContext(FiltersContext)
  const { removeQuery } = useContext(AlgoliaQueryContext)

  const [onlyInMySchool, setOnlyInMySchool] = useState(
    currentFilters.onlyInMySchool
  )
  const [onlyInMyDpt, setOnlyInMyDpt] = useState(currentFilters.onlyInMyDpt)

  const userDepartmentOption = departmentOptions.find(
    departmentOption => departmentOption.value === user.departmentCode
  )

  const setDefaultDepartmentFilter = useCallback(() => {
    if (userDepartmentOption && user.role === AdageFrontRoles.REDACTOR) {
      dispatchCurrentFilters({
        type: 'POPULATE_DEPARTMENTS_FILTER',
        departmentFilters: [userDepartmentOption],
      })
      dispatchCurrentFilters({
        type: 'POPULATE_ONLY_IN_MY_DEPARTMENT',
        departmentFilter: userDepartmentOption,
      })
    }
  }, [user, dispatchCurrentFilters, userDepartmentOption])

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
    setDefaultDepartmentFilter()
  }, [setDefaultDepartmentFilter])

  useEffect(() => {
    setOnlyInMySchool(currentFilters.onlyInMySchool)
  }, [currentFilters.onlyInMySchool])
  useEffect(() => {
    setOnlyInMyDpt(currentFilters.onlyInMyDpt)
  }, [currentFilters.onlyInMyDpt])

  const onlyInMySchoolLabel = getOnlyInMySchoolLabel(user)
  const onlyInMyDptLabel = getOnlyInMyDptLabel(user)

  return (
    <div className={className}>
      <span className="offer-filters-title">Filtrer par :</span>

      <div className="offer-filters-row">
        {onlyInMyDptLabel && (
          <BaseCheckbox
            checked={onlyInMyDpt}
            label={onlyInMyDptLabel}
            name="onlyInMyDpt"
            onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
              if (event.target.checked && userDepartmentOption) {
                dispatchCurrentFilters({
                  type: 'POPULATE_ONLY_IN_MY_DEPARTMENT',
                  departmentFilter: userDepartmentOption,
                })
              } else {
                dispatchCurrentFilters({ type: 'RESET_ONLY_IN_MY_DEPARTMENT' })
              }
            }}
          />
        )}
      </div>
      {onlyInMySchoolLabel && (
        <div className="offer-filters-row">
          <BaseCheckbox
            checked={onlyInMySchool}
            label={onlyInMySchoolLabel}
            name="onlyInMySchool"
            onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
              if (event.target.checked && userDepartmentOption) {
                dispatchCurrentFilters({
                  type: 'POPULATE_ONLY_IN_MY_SCHOOL',
                  departmentFilter: userDepartmentOption,
                })
              } else {
                dispatchCurrentFilters({ type: 'RESET_ONLY_IN_MY_SCHOOL' })
              }
            }}
          />
        </div>
      )}
      <div className="offer-filters-separator" />

      <div className="offer-filters-row">
        <MultiSelectAutocomplete
          className="offer-filters-filter"
          initialValues={currentFilters.departments}
          label="Département"
          onChange={departments =>
            dispatchCurrentFilters({
              type: 'POPULATE_DEPARTMENTS_FILTER',
              departmentFilters: [...departments],
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
              categoryFilters: [...categories],
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
              domainFilters: [...domains],
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
              studentFilters: [...students],
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
          onClick={() => handleLaunchSearchButton(currentFilters)}
        >
          Lancer la recherche
        </Button>
      </div>
    </div>
  )
}
