import React from 'react'
import classnames from 'classnames'

const CheckboxInput = props => {

  const onChange = e => props.onChange(e.target.checked)

  return <label
    className={`${classnames({required: props.required})}`}
    htmlFor={props.id}
  >
    <input {...props} type='checkbox' className='input' onChange={onChange}  />
    {props.label}
  </label>

}

export default CheckboxInput

