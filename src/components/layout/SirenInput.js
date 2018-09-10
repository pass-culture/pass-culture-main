import get from 'lodash.get'
import { BasicInput, removeWhitespaces } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'

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
    const { errors, fetchedName, readOnly, value, withFetchedName } = this.props

    console.log('this.props', this.props)

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
        {fetchedName
          ? withFetchedName && <div className="display-name">{fetchedName}</div>
          : value &&
            !errors &&
            !readOnly && <button className="button is-loading" />}
      </div>
    )
  }
}

export default connect((state, ownProps) => ({
  fetchedName: get(state, `form.${ownProps.formName}.name`),
}))(SirenInput)
