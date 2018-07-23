import React, { Component } from 'react'

import BasicInput from './BasicInput'

class NumberInput extends Component {

  onChange = e => {
    this.props.onChange(parseInt(e.target.value, 10))
  }

  render () {
    return (
      <BasicInput {...this.props}
        onChange={this.onChange}
        type='number'
      />
    )
  }
}

export default NumberInput
