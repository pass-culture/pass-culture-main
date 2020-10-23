import { isValidBIC } from 'ibantools'
import { BasicInput, mergeErrors, removeWhitespaces } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { connect } from 'react-redux'

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

BicInput.propTypes = {
  dispatch: PropTypes.func.isRequired,
  onChange: PropTypes.func.isRequired,
  value: PropTypes.string.isRequired,
}

export default connect()(BicInput)
