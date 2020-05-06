import React from 'react'
import Icon from '../../../../layout/Icon/Icon'
import PropTypes from 'prop-types'

const Checkbox = ({ checked, className, id, label, name, onChange }) => {
  return (
    <div className='fc-wrapper'>
      <input
        checked={checked}
        id={id}
        name={name}
        onChange={onChange}
        type="checkbox"
      />
      <label
        className={className}
        htmlFor={id}
      >
        {checked &&
        <Icon
          className="fc-icon-check"
          svg="ico-check-pink"
        />}
        {label}
      </label>
    </div>
  )
}

Checkbox.propTypes = {
  checked: PropTypes.bool.isRequired,
  className: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
}

export default Checkbox
