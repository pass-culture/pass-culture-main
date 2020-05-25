import React from 'react'
import PropTypes from 'prop-types'
import debounce from 'lodash.debounce'

const DELAY_BEFORE_APPLYING_FILTERS_IN_MILLISECONDS = 300

const Filters = ({ setFilters }) => {
  const applyFilters = debounce(keywords => {
    setFilters({ offerName: keywords })
  }, DELAY_BEFORE_APPLYING_FILTERS_IN_MILLISECONDS)

  function handleOnChange(event) {
    const keywords = event.target.value
    applyFilters(keywords)
  }

  return (
    <div className="bookings-recap-filters">
      <label
        className="select-filters"
        htmlFor="text-filter"
      >
        {'Offre'}
      </label>
      <input
        className="field-input field-text text-filter"
        id="text-filter"
        onChange={handleOnChange}
        placeholder={"Rechercher par nom d'offre"}
        type="text"
      />
    </div>
  )
}

Filters.propTypes = {
  setFilters: PropTypes.func.isRequired,
}

export default Filters
