import React from 'react'
import PropTypes from 'prop-types'

const FilterByOmniSearch = ({
  keywords,
  omniSearchSelectOptions,
  onHandleOmniSearchChange,
  onHandleOmniSearchCriteriaChange,
  placeholderText,
}) => {
  return (
    <div className="fw-first-line">
      <select
        className="fw-booking-text-filters-select"
        onBlur={onHandleOmniSearchCriteriaChange}
        onChange={onHandleOmniSearchCriteriaChange}
      >
        {omniSearchSelectOptions.map(selectOption => (
          <option
            key={selectOption.id}
            value={selectOption.id}
          >
            {selectOption.selectOptionText}
          </option>
        ))}
      </select>

      <span className="vertical-bar" />

      <input
        className="fw-booking-text-filters-input"
        id="text-filter-input"
        onChange={onHandleOmniSearchChange}
        placeholder={placeholderText}
        type="text"
        value={keywords}
      />
    </div>
  )
}

FilterByOmniSearch.propTypes = {
  keywords: PropTypes.string.isRequired,
  omniSearchSelectOptions: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      selectOptionText: PropTypes.string.isRequired,
    })
  ).isRequired,
  onHandleOmniSearchChange: PropTypes.func.isRequired,
  onHandleOmniSearchCriteriaChange: PropTypes.func.isRequired,
  placeholderText: PropTypes.string.isRequired,
}

export default FilterByOmniSearch
