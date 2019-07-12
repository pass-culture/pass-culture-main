import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FieldErrors from '../FieldErrors'

const noOperation = () => {}

class HiddenField extends Component {
  renderField = ({ input, meta }) => (
    <div>
      <input
        type="hidden"
        {...input}
      />
      <FieldErrors meta={meta} />
    </div>
  )

  render() {
    const { name, validator } = this.props

    return (<Field
      name={name}
      render={this.renderField}
      validate={validator}
            />)
  }
}

HiddenField.defaultProps = {
  validator: noOperation,
}

HiddenField.propTypes = {
  name: PropTypes.string.isRequired,
  validator: PropTypes.func,
}

export default HiddenField
