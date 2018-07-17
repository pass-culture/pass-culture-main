import React from 'react'
import { removeWhitespaces, formatSiren } from '../../../utils/string'
import BasicInput from './BasicInput'

const SirenInput = props => {

  const input = <BasicInput {...props} type='text' />

  if (typeof props.fetchedName !== 'string') return input
  return <div className='with-display-name'>
    {input}
    <div className='display-name'>{props.fetchedName}</div>
  </div>
}

SirenInput.displayValue = formatSiren
SirenInput.storeValue = removeWhitespaces

export default SirenInput

