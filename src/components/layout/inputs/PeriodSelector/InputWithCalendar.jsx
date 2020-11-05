import PropTypes from 'prop-types'
import React from 'react'

const InputWithCalendar = props => {
  const { customClass, ...inputProperties } = props
  delete inputProperties.props

  return (
    <label className={customClass}>
      <input
        {...inputProperties}
        type="text"
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
