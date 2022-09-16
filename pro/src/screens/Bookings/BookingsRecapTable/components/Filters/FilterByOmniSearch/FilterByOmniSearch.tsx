import React, { ChangeEvent, useMemo } from 'react'

import { Audience } from 'core/shared'

import { BookingsFilters } from '../../../types'
import { EMPTY_FILTER_VALUE } from '../_constants'

import {
  COLLECTIVE_OMNISEARCH_FILTERS,
  INDIVIDUAL_OMNISEARCH_FILTERS,
} from './constants'
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

const FilterByOmniSearch = ({
  isDisabled,
  keywords,
  selectedOmniSearchCriteria,
  updateFilters,
  audience,
}: FilterByOmniSearchProps) => {
  const omnisearchFilters = useMemo(
    () =>
      audience === Audience.INDIVIDUAL
        ? INDIVIDUAL_OMNISEARCH_FILTERS
        : COLLECTIVE_OMNISEARCH_FILTERS,
    [audience]
  )

  function updateOmniSearchKeywords(
    omniSearchCriteria: string,
    keywords: string
  ) {
    const cleanedOmnisearchFilters: BookingOmniSearchFilters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
      bookingInstitution: EMPTY_FILTER_VALUE,
    }

    const omniSearchStateKey = omnisearchFilters.find(
      criteria => criteria.id === omniSearchCriteria
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

  function handleOmniSearchChange(event: ChangeEvent<HTMLInputElement>) {
    updateOmniSearchKeywords(selectedOmniSearchCriteria, event.target.value)
  }

  function handleOmniSearchCriteriaChange(
    event: ChangeEvent<HTMLSelectElement>
  ) {
    const newOmniSearchCriteria = event.target.value.toLowerCase()
    updateOmniSearchKeywords(newOmniSearchCriteria, keywords)
  }

  const placeholderText = omnisearchFilters.find(
    criteria => criteria.id === selectedOmniSearchCriteria
  )?.placeholderText

  return (
    <div className={`fw-first-line ${isDisabled ? 'disabled' : ''}`}>
      <select
        className="fw-booking-text-filters-select"
        disabled={isDisabled}
        onBlur={handleOmniSearchCriteriaChange}
        onChange={handleOmniSearchCriteriaChange}
      >
        {omnisearchFilters.map(selectOption => (
          <option key={selectOption.id} value={selectOption.id}>
            {selectOption.selectOptionText}
          </option>
        ))}
      </select>

      <span className="vertical-bar" />

      <input
        className="fw-booking-text-filters-input"
        disabled={isDisabled}
        id="text-filter-input"
        onChange={handleOmniSearchChange}
        placeholder={placeholderText}
        type="text"
        value={keywords}
      />
    </div>
  )
}

export default FilterByOmniSearch
