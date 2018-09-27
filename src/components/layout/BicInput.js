import get from 'lodash.get'
import { BasicInput, removeWhitespaces } from 'pass-culture-shared'
import React, { PureComponent, Fragment } from 'react'
import { connect } from 'react-redux'

class BicInput extends PureComponent {
  onChange = event => {
    event.persist()
    this.props.onChange(event.target.value, {
      event,
      isSagaCalling: false,
    })
  }

  render() {
    const { errors, value } = this.props

    return (
      <BasicInput
        {...this.props}
        onChange={this.onChange}
        type="text"
        value={removeWhitespaces(value)}
      />
    )
  }
}

export default connect((state, ownProps) => ({
  fetchedName: get(state, `form.${ownProps.formName}.name`),
}))(BicInput)
