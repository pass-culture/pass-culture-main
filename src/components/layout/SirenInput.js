import { BasicInput } from 'pass-culture-shared'
import React from 'react'

import { removeWhitespaces, formatSiren } from '../../utils/string'

const SirenInput = props => {

  const onInputChange = e => props.onChange(removeWhitespaces(e.target.value))

  const input = <BasicInput {...props} type='text' onChange={onInputChange} value={formatSiren(props.value)} />

  if (typeof props.fetchedName !== 'string') return input
  return (
    <div className='with-display-name'>
      {input}
      <div className='display-name'>
        {props.fetchedName}
      </div>
    </div>
  )
}

export default SirenInput
