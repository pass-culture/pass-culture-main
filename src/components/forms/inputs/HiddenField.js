import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'

const noop = () => {}

class HiddenField extends Component {
  renderField = ({ input, meta }) => {
    const { ...inputProps } = this.props

    return (
      <div>
        <input
          type="hidden"
          {...input}
          {...inputProps}
        />
        <FormError meta={meta} />
      </div>
    )
  }

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
  validator: noop,
}

HiddenField.propTypes = {
  name: PropTypes.string.isRequired,
  validator: PropTypes.func,
}

export default HiddenField
