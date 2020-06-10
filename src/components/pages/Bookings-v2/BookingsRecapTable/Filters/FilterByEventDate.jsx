import React from 'react'
import InputWithCalendar from './InputWithCalendar'
import PropTypes from 'prop-types'
import DatePicker from 'react-datepicker'

const FilterByEventDate = ({ onHandleOfferDateChange, selectedOfferDate }) => {
  return (
    <div className="fw-offer-date">
      <label
        className="fw-offer-date-label"
        htmlFor="select-filter-date"
      >
        {"Date de l'évènement"}
      </label>
      <div className="fw-offer-date-picker">
        <DatePicker
          className="fw-offer-date-input"
          customInput={<InputWithCalendar customClass="field-date-only" />}
          dropdownMode="select"
          id="select-filter-date"
          onChange={onHandleOfferDateChange}
          placeholderText="JJ/MM/AAAA"
          selected={selectedOfferDate}
        />
      </div>
    </div>
  )
}

FilterByEventDate.propTypes = {
  onHandleOfferDateChange: PropTypes.func.isRequired,
  selectedOfferDate: PropTypes.oneOfType([PropTypes.shape(), PropTypes.string]).isRequired,
}

export default FilterByEventDate
