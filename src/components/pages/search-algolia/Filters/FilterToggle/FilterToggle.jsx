import React from 'react'
import PropTypes from 'prop-types'

const FilterToggle = ({ checked, id, name, onChange }) => {
  return (
    <div className="ft-wrapper">
      <input
        checked={checked}
        className="ft-checkbox"
        id={id}
        name={name}
        onChange={onChange}
        type="checkbox"
      />
      <label
        className={checked ? 'ft-label-on' : 'ft-label-off'}
        htmlFor={id}
      >
        <span className="ft-button" />
      </label>
    </div>
  )
}

FilterToggle.propTypes = {
  checked: PropTypes.bool.isRequired,
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
}

export default FilterToggle
