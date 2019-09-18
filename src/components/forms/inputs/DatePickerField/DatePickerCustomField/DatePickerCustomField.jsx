import React from 'react'
import PropTypes from 'prop-types'
import classnames from 'classnames'

import Icon from '../../../../layout/Icon/Icon'

const DatePickerCustomField = props => {
  const { readOnly, ref, value } = props

  return (
    <div
      className={classnames('react-datepicker__input-container_wrapper', {
        selected: value,
      })}
    >
      <input
        {...props}
        className="form-datepicker-input"
        readOnly
        ref={ref}
      />
      {!readOnly && (
        <div className="calendar-icon">
          <Icon
            alt="Dates"
            svg="ico-calendar"
          />
        </div>
      )}
    </div>
  )
}

DatePickerCustomField.defaultProps = {
  readOnly: false,
  ref: null,
  value: null,
}

DatePickerCustomField.propTypes = {
  readOnly: PropTypes.bool,
  ref: PropTypes.shape(),
  value: PropTypes.string,
}

export default DatePickerCustomField
