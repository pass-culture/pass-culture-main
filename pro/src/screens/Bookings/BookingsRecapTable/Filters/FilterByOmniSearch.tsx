import cn from 'classnames'
import React, { ChangeEvent } from 'react'

import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import { Audience } from 'core/shared/types'
import { SelectOption } from 'custom_types/form'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
import { BaseInput } from 'ui-kit/form/shared/BaseInput/BaseInput'

import { BookingsFilters } from '../types'

import {
  EMPTY_FILTER_VALUE,
  COLLECTIVE_OMNISEARCH_FILTERS,
  INDIVIDUAL_OMNISEARCH_FILTERS,
} from './constants'
import styles from './FilterByOmniSearch.module.scss'
import { BookingOmniSearchFilters } from './types'

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

  const placeholderText = omnisearchFilters.find(
    (criteria) => criteria.id === selectedOmniSearchCriteria
  )?.placeholderText

  return (
    <fieldset
      className={cn(styles['omnisearch-container'], {
        [styles['omnisearch-container-disabled']]: isDisabled,
      })}
    >
      <legend className="visually-hidden">
        Rechercher dans les réservations
      </legend>
      <label htmlFor="omnisearch-criteria" className="visually-hidden">
        Informations dans laquelle rechercher
      </label>
      <SelectInput
        name="omnisearch-criteria"
        className={styles['omnisearch-filter-select']}
        disabled={isDisabled}
        onBlur={handleOmniSearchCriteriaChange}
        onChange={handleOmniSearchCriteriaChange}
        value={selectedOmniSearchCriteria}
        options={omnisearchFiltersOptions}
      />

      <span className={styles['vertical-bar']} />

      <label htmlFor="text-filter-input" className="visually-hidden">
        Texte à rechercher
      </label>

      <BaseInput
        type="text"
        className={styles['omnisearch-filter-input']}
        disabled={isDisabled}
        id="text-filter-input"
        onChange={handleOmniSearchChange}
        placeholder={placeholderText}
        value={keywords}
      />
    </fieldset>
  )
}
