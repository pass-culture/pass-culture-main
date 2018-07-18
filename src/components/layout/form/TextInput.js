import React from 'react'

import BasicInput from './BasicInput'

const TextInput = props => {
  const onInputChange = e => props.onChange(e.target.value)

  return <BasicInput {...props} onChange={onInputChange}/>
}

export default TextInput

