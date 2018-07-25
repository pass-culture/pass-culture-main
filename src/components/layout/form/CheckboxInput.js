import React from 'react'
import classnames from 'classnames'

import BasicInput from './BasicInput'

const CheckboxInput = props => {

  const onInputChange = e => props.onChange(e.target.checked)

  return (
    <label
      className={`${classnames({required: props.required})}`}
      htmlFor={props.id}>
      <BasicInput {...props} type='checkbox' className='input' onChange={onInputChange}  />
      {props.label}
    </label>
  )

}

export default CheckboxInput
