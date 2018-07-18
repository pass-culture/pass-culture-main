import React from 'react'

const BasicInput = props => {

  return <input
    aria-describedby={props['aria-describedby']}
    autoComplete={props.autoComplete}
    className={`input is-${props.size}`}
    id={props.id}
    name={props.name}
    onChange={props.onChange}
    required={props.required}
    readOnly={props.readOnly}
    type={props.type}
    value={props.value}
  />
}

export default BasicInput

