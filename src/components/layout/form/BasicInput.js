import React from 'react'
import PropTypes from 'prop-types';

const BasicInput = props => {

  return <input
    aria-describedby={props['aria-describedby']}
    autoComplete={props.autoComplete}
    className={`input is-${props.size}`}
    id={props.id}
    name={props.name}
    onChange={props.onChange}
    required={props.required}
    type={props.type}
    value={props.value}
  />
}

BasicInput.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  onChange: PropTypes.func.isRequired,
}
export default BasicInput

