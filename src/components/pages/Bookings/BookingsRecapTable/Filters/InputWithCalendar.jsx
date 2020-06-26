import React from 'react'
import PropTypes from 'prop-types'

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
