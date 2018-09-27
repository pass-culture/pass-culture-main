import get from 'lodash.get'
import { BasicInput, mergeErrors, removeWhitespaces } from 'pass-culture-shared'
import React, { PureComponent, Fragment } from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { isValidBIC } from 'ibantools'

class BicInput extends PureComponent {
  constructor(props) {
    super(props)
    this.mergeErrors = bindActionCreators(mergeErrors, props.dispatch)
  }

  onChange = event => {
    event.persist()
    const value = removeWhitespaces(event.target.value)
    this.props.onChange(value, { event })

    if (!isValidBIC(value)) {
      this.mergeErrors('offerer', { bic: ['BIC invalide'] })
    }
  }

  render() {
    const { value } = this.props
    return (
      <BasicInput
        {...this.props}
        onChange={this.onChange}
        type="text"
        value={value.toUpperCase()}
      />
    )
  }
}

export default connect()(BicInput)
