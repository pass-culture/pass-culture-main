import React from 'react'

const BasicInput = props => {

  const onInputChange = e => props.onChange(e.target.value)

  return <input
    aria-describedby={props['aria-describedby']}
    autoComplete={props.autoComplete}
    className={`input is-${props.size}`}
    id={props.id}
    onChange={onInputChange}
    required={props.required}
    type={props.type}
    value={props.value}
  />
}

export default BasicInput

