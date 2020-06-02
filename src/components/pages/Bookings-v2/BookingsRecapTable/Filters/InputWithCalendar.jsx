import React from 'react'
import Icon from '../../../../layout/Icon'
import PropTypes from 'prop-types'

const InputWithCalendar = props => {
  const { className, customClass, placeholder, value } = props

  return (
    <label className={customClass}>
      <input
        className={className}
        placeholder={placeholder}
        type="text"
        value={value}
      />
      <div className="flex-auto" />
      <Icon
        alt="Horaires"
        svg="ico-calendar"
      />
    </label>
  )
}

InputWithCalendar.defaultProps = {
  props: {},
}

InputWithCalendar.propTypes = {
  props: PropTypes.shape({
    customClass: PropTypes.string,
  }),
}

export default InputWithCalendar
