import React from 'react'
import Icon from '../../../../layout/Icon'
import PropTypes from 'prop-types'

const InputWithCalendar = props => {
  const { customClass, ...inputProps } = props

  return (
    <label className={customClass}>
      <input
        {...inputProps}
        type="text"
      />
      <div className="flex-auto" />
      <Icon
        alt="Horaires"
        svg="ico-calendar"
      />
    </label>
  )
}

InputWithCalendar.propTypes = {
  props: PropTypes.shape({
    customClass: PropTypes.string,
  }).isRequired,
}

export default InputWithCalendar
