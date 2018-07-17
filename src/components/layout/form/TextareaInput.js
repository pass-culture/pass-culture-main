import React from 'react'
import Textarea from 'react-autosize-textarea'

const TextareaInput = props => {

  const onChange = e => props.onChange(e.target.value)

  return <Textarea {...props} onChange={onChange} className={`textarea is-${props.size}`} />
}

export default TextareaInput

