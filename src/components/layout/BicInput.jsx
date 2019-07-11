import { BasicInput, mergeErrors, removeWhitespaces } from 'pass-culture-shared'
import React, { PureComponent } from 'react'
import { connect } from 'react-redux'
import { isValidBIC } from 'ibantools'

class BicInput extends PureComponent {
  handleOnChange = event => {
    event.persist()
    const value = removeWhitespaces(event.target.value)
    const { onChange } = this.props
    onChange(value, { event })

    if (!isValidBIC(value)) {
      const { dispatch } = this.props
      dispatch(mergeErrors('offerer', { bic: ['BIC invalide'] }))
    }
  }

  render() {
    const { value } = this.props
    return (
      <BasicInput
        {...this.props}
        onChange={this.handleOnChange}
        type="text"
        value={value.toUpperCase()}
      />
    )
  }
}

export default connect()(BicInput)
