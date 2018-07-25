import React from 'react'

import BasicInput from './BasicInput'

const TextInput = props => {
  const onInputChange = e => props.onChange(e.target.value)

  const guessAutoComplete = () => {
    if (props.name === 'email') return 'email'
  }

  return <BasicInput {...props} onChange={onInputChange} autoComplete={guessAutoComplete()} />
}

export default TextInput

