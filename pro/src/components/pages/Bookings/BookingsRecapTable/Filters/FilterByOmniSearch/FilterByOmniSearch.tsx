import React, { ChangeEvent } from 'react'

import { BookingsFilters } from '../../types'
import { EMPTY_FILTER_VALUE } from '../_constants'

interface FilterByOmniSearchProps {
  isDisabled: boolean
  keywords: string
  selectedOmniSearchCriteria: string
  updateFilters: (
    filters: Partial<BookingsFilters>,
    updatedContent: { keywords: string; selectedOmniSearchCriteria: string }
  ) => void
}

type OmnisearchFilter = {
  id: string
  placeholderText: string
  stateKey: keyof Pick<
    BookingsFilters,
    'bookingBeneficiary' | 'bookingToken' | 'offerISBN' | 'offerName'
  >
  selectOptionText: string
}

const OMNISEARCH_FILTERS: OmnisearchFilter[] = [
  {
    id: 'offre',
    placeholderText: "Rechercher par nom d'offre",
    stateKey: 'offerName',
    selectOptionText: 'Offre',
  },
  {
    id: 'bénéficiaire',
    placeholderText: 'Rechercher par nom ou email',
    stateKey: 'bookingBeneficiary',
    selectOptionText: 'Bénéficiaire',
  },
  {
    id: 'isbn',
    placeholderText: 'Rechercher par ISBN',
    stateKey: 'offerISBN',
    selectOptionText: 'ISBN',
  },
  {
    id: 'contremarque',
    placeholderText: 'Rechercher par contremarque',
    stateKey: 'bookingToken',
    selectOptionText: 'Contremarque',
  },
]

const FilterByOmniSearch = ({
  isDisabled,
  keywords,
  selectedOmniSearchCriteria,
  updateFilters,
}: FilterByOmniSearchProps) => {
  function updateOmniSearchKeywords(
    omniSearchCriteria: string,
    keywords: string
  ) {
    const cleanedOmnisearchFilters: Pick<
      BookingsFilters,
      'bookingBeneficiary' | 'bookingToken' | 'offerISBN' | 'offerName'
    > = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
    }

    const omniSearchStateKey = OMNISEARCH_FILTERS.find(
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

  const placeholderText = OMNISEARCH_FILTERS.find(
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
        {OMNISEARCH_FILTERS.map(selectOption => (
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
