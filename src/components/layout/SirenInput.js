import {
  BasicInput,
  removeWhitespaces
} from 'pass-culture-shared'
import React, { Component } from 'react'

import { formatSiren } from '../../utils/string'

class SirenInput extends Component  {

  onChange = e => {
    this.props.onChange(
      removeWhitespaces(e.target.value),
      { isSagaCalling: true }
    )
  }

  render () {

    const {
      fetchedName,
      value
    } = this.props

    const $input = (
      <BasicInput
        {...this.props}
        onChange={this.onChange}
        type='text'
        value={formatSiren(value)} />
    )

    if (typeof fetchedName !== 'string') return $input
    return (
      <div className='with-display-name'>
        {$input}
        <div className='display-name'>
          {fetchedName}
        </div>
      </div>
    )
  }
}

export default SirenInput
