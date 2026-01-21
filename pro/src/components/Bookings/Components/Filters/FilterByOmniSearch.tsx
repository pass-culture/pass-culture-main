import cn from 'classnames'
import type { ChangeEvent } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { SearchInput } from '@/design-system/SearchInput/SearchInput'
import { Select } from '@/ui-kit/form/Select/Select'

import type { BookingsFilters } from '../types'
import { EMPTY_FILTER_VALUE, INDIVIDUAL_OMNISEARCH_FILTERS } from './constants'
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
}

export const FilterByOmniSearch = ({
  isDisabled,
  keywords,
  selectedOmniSearchCriteria,
  updateFilters,
}: FilterByOmniSearchProps) => {
  const { logEvent } = useAnalytics()

  const omnisearchFiltersOptions = INDIVIDUAL_OMNISEARCH_FILTERS

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

    const omniSearchStateKey = omnisearchFiltersOptions.find(
      (criteria) => criteria.value === omniSearchCriteria
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

      <div className={styles['omnisearch-row']}>
        <Select
          label="Critère"
          name="omnisearch-criteria"
          className={styles['omnisearch-filter-select']}
          disabled={isDisabled}
          onBlur={handleOmniSearchCriteriaChange}
          onChange={handleOmniSearchCriteriaChange}
          value={selectedOmniSearchCriteria}
          options={omnisearchFiltersOptions}
        />

        <div className={styles['omnisearch-search-input']}>
          <SearchInput
            name="search"
            label="Recherche"
            disabled={isDisabled}
            onChange={handleOmniSearchChange}
            value={keywords}
          />
        </div>
      </div>
    </fieldset>
  )
}
