import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FieldError from 'components/layout/form/FieldError'

const noop = () => {}

export const HiddenField = ({ name, validator }) => (
  <Field
    name={name}
    validate={validator}
    render={({ input, meta }) => (
      <div>
        <input type="hidden" {...input} />
        <FieldError meta={meta} />
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
