import React from 'react'

import BasicInput from './BasicInput'

const NumberInput = props => {

  const onChange = e => props.onChange(parseInt(e.target.value))

  return <BasicInput {...props} type='number' onChange={onChange} min={this.props.min || 0}/>
}

export default NumberInput

