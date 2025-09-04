import cn from 'classnames'
import strokeSearchIcon from 'icons/stroke-search.svg'
import { type ChangeEvent, useId } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Audience } from '@/commons/core/shared/types'
import type { SelectOption } from '@/commons/custom_types/form'
import { TextInput } from '@/design-system/TextInput/TextInput'
import { SelectInput } from '@/ui-kit/form/shared/BaseSelectInput/SelectInput'

import type { BookingsFilters } from '../types'
import {
  COLLECTIVE_OMNISEARCH_FILTERS,
  EMPTY_FILTER_VALUE,
  INDIVIDUAL_OMNISEARCH_FILTERS,
} from './constants'
import styles from './FilterByOmniSearch.module.scss'
import type { BookingOmniSearchFilters } from './types'

export interface FilterByOmniSearchProps {
  isDisabled: boolean
  keywords: string
  selectedOmniSearchCriteria: string
  updateFilters: (
    filters: Partial<BookingsFilters>,
    updatedContent: { keywords: string; selectedOmniSearchCriteria: string }
  ) => void
  audience: Audience
}

export const FilterByOmniSearch = ({
  isDisabled,
  keywords,
  selectedOmniSearchCriteria,
  updateFilters,
  audience,
}: FilterByOmniSearchProps) => {
  const { logEvent } = useAnalytics()

  const criteriaSelectId = useId()

  const omnisearchFilters =
    audience === Audience.INDIVIDUAL
      ? INDIVIDUAL_OMNISEARCH_FILTERS
      : COLLECTIVE_OMNISEARCH_FILTERS

  const omnisearchFiltersOptions: SelectOption[] = omnisearchFilters.map(
    (omnisearchFilter) => ({
      value: omnisearchFilter.id,
      label: omnisearchFilter.selectOptionText,
    })
  )

  const updateOmniSearchKeywords = (
    omniSearchCriteria: string,
    keywords: string
  ) => {
    const cleanedOmnisearchFilters: BookingOmniSearchFilters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
      bookingInstitution: EMPTY_FILTER_VALUE,
      bookingId: EMPTY_FILTER_VALUE,
    }

    const omniSearchStateKey = omnisearchFilters.find(
      (criteria) => criteria.id === omniSearchCriteria
    )?.stateKey
    if (omniSearchStateKey) {
      cleanedOmnisearchFilters[omniSearchStateKey] = keywords
    }

    const updatedSelectedContent = {
      keywords: keywords,
      selectedOmniSearchCriteria: omniSearchCriteria,
    }
    updateFilters(cleanedOmnisearchFilters, updatedSelectedContent)
  }

  const handleOmniSearchChange = (event: ChangeEvent<HTMLInputElement>) => {
    updateOmniSearchKeywords(selectedOmniSearchCriteria, event.target.value)
  }

  const handleOmniSearchCriteriaChange = (
    event: ChangeEvent<HTMLSelectElement>
  ) => {
    const newOmniSearchCriteria = event.target.value.toLowerCase()
    updateOmniSearchKeywords(newOmniSearchCriteria, keywords)
    logEvent(Events.CLICKED_OMNI_SEARCH_CRITERIA, {
      from: location.pathname,
      criteria: newOmniSearchCriteria,
    })
  }

  return (
    <fieldset
      className={cn(styles['omnisearch-container'], {
        [styles['omnisearch-container-disabled']]: isDisabled,
      })}
    >
      <legend className={styles['visually-hidden']}>
        Rechercher dans les réservations
      </legend>

      <div>
        <label
          className={styles['omnisearch-criteria-label']}
          htmlFor={criteriaSelectId}
        >
          Critère
        </label>
        <SelectInput
          name="omnisearch-criteria"
          className={styles['omnisearch-filter-select']}
          disabled={isDisabled}
          id={criteriaSelectId}
          onBlur={handleOmniSearchCriteriaChange}
          onChange={handleOmniSearchCriteriaChange}
          value={selectedOmniSearchCriteria}
          options={omnisearchFiltersOptions}
        />
      </div>

      <div className={styles['omnisearch-search-input']}>
        <TextInput
          type="search"
          name="search"
          label="Recherche"
          icon={strokeSearchIcon}
          disabled={isDisabled}
          onChange={handleOmniSearchChange}
          value={keywords}
        />
      </div>
    </fieldset>
  )
}
