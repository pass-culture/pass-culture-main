import { BasicInput, removeWhitespaces } from 'pass-culture-shared'
import React, { Component } from 'react'

import { formatSiren } from '../../utils/string'

class SirenInput extends Component {
  onChange = event => {
    event.persist()
    this.props.onChange(removeWhitespaces(event.target.value), {
      event,
      isSagaCalling: true,
    })
  }

  render() {
    const { errors, fetchedName, value } = this.props

    const $input = (
      <BasicInput
        {...this.props}
        onChange={this.onChange}
        type="text"
        value={formatSiren(value)}
      />
    )

    return (
      <div className="with-display-name">
        {$input}
        {fetchedName ? (
          <div className="display-name">{fetchedName}</div>
        ) : (
          value && !errors && <button className="button is-loading" />
        )}
      </div>
    )
  }
}

export default SirenInput
