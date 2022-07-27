import PropTypes from 'prop-types'
import React, { forwardRef } from 'react'

const InputWithCalendar = forwardRef(function InputWithCalendar(props, ref) {
  const { customClass, ariaLabel, ...inputProperties } = props
  delete inputProperties.props

  return (
    <div className={customClass}>
      <input
        aria-label={ariaLabel}
        {...inputProperties}
        ref={ref}
        type="text"
      />
    </div>
  )
})

InputWithCalendar.defaultProps = {
  ariaLabel: undefined,
  props: {},
}

InputWithCalendar.propTypes = {
  ariaLabel: PropTypes.string,
  customClass: PropTypes.string.isRequired,
  props: PropTypes.shape({
    customClass: PropTypes.string,
  }),
}

export default InputWithCalendar
