import PropTypes from 'prop-types'
import React from 'react'

import { EMPTY_FILTER_VALUE } from '../_constants'

const OMNISEARCH_FILTERS = [
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
}) => {
  function updateOmniSearchKeywords(omniSearchCriteria, keywords) {
    const cleanedOmnisearchFilters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
    }

    const omniSearchStateKey = OMNISEARCH_FILTERS.find(
      criteria => criteria.id === omniSearchCriteria
    ).stateKey
    cleanedOmnisearchFilters[omniSearchStateKey] =
      keywords && keywords.length > 0 ? keywords : EMPTY_FILTER_VALUE

    const updatedSelectedContent = {
      keywords: keywords,
      selectedOmniSearchCriteria: omniSearchCriteria,
    }
    updateFilters(cleanedOmnisearchFilters, updatedSelectedContent)
  }

  function handleOmniSearchChange(event) {
    updateOmniSearchKeywords(selectedOmniSearchCriteria, event.target.value)
  }

  function handleOmniSearchCriteriaChange(event) {
    const newOmniSearchCriteria = event.target.value.toLowerCase()
    updateOmniSearchKeywords(newOmniSearchCriteria, keywords)
  }

  const placeholderText = OMNISEARCH_FILTERS.find(
    criteria => criteria.id === selectedOmniSearchCriteria
  ).placeholderText

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

FilterByOmniSearch.propTypes = {
  isDisabled: PropTypes.bool.isRequired,
  keywords: PropTypes.string.isRequired,
  selectedOmniSearchCriteria: PropTypes.string.isRequired,
  updateFilters: PropTypes.func.isRequired,
}

export default FilterByOmniSearch
