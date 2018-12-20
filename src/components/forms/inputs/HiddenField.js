import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'

const noop = () => {}

const HiddenField = ({ name, validator, ...inputProps }) => (
  <Field
    name={name}
    validate={validator}
    render={({ input, meta }) => (
      <div>
        <input type="hidden" {...input} {...inputProps} />
        <FormError meta={meta} />
      </div>
    )}
  />
)

HiddenField.defaultProps = {
  validator: noop,
}

HiddenField.propTypes = {
  name: PropTypes.string.isRequired,
  validator: PropTypes.func,
}

export default HiddenField
