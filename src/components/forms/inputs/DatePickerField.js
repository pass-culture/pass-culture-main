import React from 'react'
import PropTypes from 'prop-types'
import DatePicker from 'react-datepicker'

const DatePickerField = ({
  clearable,
  container,
  format,
  id,
  locale,
  minDate,
  placeholderText,
  onChange,
  selected,
}) => (
  <DatePicker
    id={id}
    locale={locale}
    dateFormat={format}
    isClearable={clearable}
    minDate={minDate}
    onChange={onChange}
    // popperPlacement="bottom-start"
    selected={selected}
    placeholderText={placeholderText}
    popperContainer={container}
    popperPlacement="top-end"
    popperClassName="search-by-dates"
    popperModifiers={{
      offset: {
        enabled: true,
        offset: '5px, 10px',
      },
      preventOverflow: {
        boundariesElement: 'viewport',
        enabled: true,
        escapeWithReference: false, // force popper to stay in viewport (even when input is scrolled out of view)
      },
    }}
  />
)

DatePickerField.defaultProps = {
  clearable: true,
  container: null,
  format: 'DD/MM/YYYY',
  locale: 'fr',
  minDate: null,
  placeholderText: 'Par date...',
  selected: null,
}

DatePickerField.propTypes = {
  clearable: PropTypes.bool,
  container: PropTypes.func,
  format: PropTypes.string,
  id: PropTypes.string.isRequired,
  locale: PropTypes.string,
  minDate: PropTypes.object,
  onChange: PropTypes.func.isRequired,
  placeholderText: PropTypes.string,
  selected: PropTypes.object,
}

export default DatePickerField
