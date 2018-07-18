import React from 'react'
import Textarea from 'react-autosize-textarea'

const TextareaInput = props => {

  const onChange = e => props.onChange(e.target.value)

  return <Textarea
    aria-describedby={props['aria-describedby']}
    autoComplete={props.autoComplete}
    className={`textarea is-${props.size}`}
    id={props.id}
    name={props.name}
    required={props.required}
    type={props.type}
    value={props.value}
    onChange={onChange}
    readOnly={props.readOnly}
  />
}

export default TextareaInput

