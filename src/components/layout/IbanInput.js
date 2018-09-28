import { BasicInput, mergeErrors, removeWhitespaces } from 'pass-culture-shared'
import React, { PureComponent } from 'react'
import { connect } from 'react-redux'
import { isValidIBAN, friendlyFormatIBAN } from 'ibantools'

class IbanInput extends PureComponent {
  onChange = event => {
    event.persist()
    const value = removeWhitespaces(event.target.value)
    this.props.onChange(value, { event })

    if (!isValidIBAN(value)) {
      this.props.mergeErrors('offerer', { iban: ['IBAN invalide'] })
    }
  }

  render() {
    return (
      <BasicInput
        {...this.props}
        onChange={this.onChange}
        type="text"
        value={friendlyFormatIBAN(this.props.value)}
      />
    )
  }
}

const mapDispatchToProps = { mergeErrors }

export default connect(
  null,
  mapDispatchToProps
)(IbanInput)
