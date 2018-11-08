import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import { FormError } from '../FormError'

const noop = () => {}

const HiddenField = ({ name, validator }) => (
  <Field
    name={name}
    validate={validator}
    render={({ input, meta }) => (
      <div>
        <input type="hidden" {...input} />
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
