import PropTypes from 'prop-types'
import React from 'react'
import DatePicker from 'react-datepicker'

import InputWithCalendar from 'components/layout/inputs/PeriodSelector/InputWithCalendar'

const FilterByEventDate = ({ updateFilters, selectedOfferDate }) => {
  function handleOfferDateChange(offerDate) {
    updateFilters({ offerDate: offerDate })
  }

  return (
    <div className="fw-offer-date">
      <label
        className="fw-offer-date-label"
        htmlFor="select-filter-date"
      >
        {'Date de l’évènement'}
      </label>
      <div className="fw-offer-date-picker">
        <DatePicker
          className="fw-offer-date-input"
          customInput={<InputWithCalendar customClass="field-date-only" />}
          dateFormat="dd/MM/yyyy"
          dropdownMode="select"
          id="select-filter-date"
          onChange={handleOfferDateChange}
          placeholderText="JJ/MM/AAAA"
          selected={selectedOfferDate}
        />
      </div>
    </div>
  )
}

FilterByEventDate.propTypes = {
  selectedOfferDate: PropTypes.oneOfType([PropTypes.shape(), PropTypes.string]).isRequired,
  updateFilters: PropTypes.func.isRequired,
}

export default FilterByEventDate
