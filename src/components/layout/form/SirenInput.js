import React from 'react'
import { removeWhitespaces, formatSiren } from '../../../utils/string'
import BasicInput from './BasicInput'

const SirenInput = props => {

  const onInputChange = e => props.onChange(e.target.value)

  const input = <BasicInput {...props} type='text' onChange={onInputChange} />

  if (typeof props.fetchedName !== 'string') return input
  return <div className='with-display-name'>
    {input}
    <div className='display-name'>{props.fetchedName}</div>
  </div>
}

SirenInput.displayValue = formatSiren
SirenInput.storeValue = removeWhitespaces

export default SirenInput

