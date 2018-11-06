import { BasicInput, mergeErrors, removeWhitespaces } from 'pass-culture-shared'
import React, { PureComponent } from 'react'
import { connect } from 'react-redux'
import { isValidBIC } from 'ibantools'

class BicInput extends PureComponent {
  onChange = event => {
    event.persist()
    const value = removeWhitespaces(event.target.value)
    this.props.onChange(value, { event })

    if (!isValidBIC(value)) {
      this.props.dispatch(mergeErrors('offerer', { bic: ['BIC invalide'] }))
    }
  }

  render() {
    return (
      <BasicInput
        {...this.props}
        onChange={this.onChange}
        type="text"
        value={this.props.value.toUpperCase()}
      />
    )
  }
}

export default connect()(BicInput)
