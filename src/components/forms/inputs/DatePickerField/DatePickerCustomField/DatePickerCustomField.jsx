import React from 'react'
import PropTypes from 'prop-types'
import classnames from 'classnames'

const DatePickerCustomField = props => {
  const { ref, value } = props

  return (
    <div
      className={classnames('react-datepicker__input-container_wrapper', {
        selected: value,
      })}
    >
      <input
        {...props}
        className="pc-final-form-datepicker-input"
        readOnly
        ref={ref}
      />
    </div>
  )
}

DatePickerCustomField.defaultProps = {
  ref: null,
  value: null,
}

DatePickerCustomField.propTypes = {
  ref: PropTypes.shape(),
  value: PropTypes.string,
}

export default DatePickerCustomField
