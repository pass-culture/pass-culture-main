import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FieldErrors from 'components/layout/form/FieldErrors'

const noOperation = () => {}

export const HiddenField = ({ name, validator }) => (
  <Field
    name={name}
    render={({ input, meta }) => (
      <div>
        <input
          type="hidden"
          {...input}
        />
        <FieldErrors meta={meta} />
      </div>
    )}
    validate={validator}
  />
)

HiddenField.defaultProps = {
  validator: noOperation,
}

HiddenField.propTypes = {
  name: PropTypes.string.isRequired,
  validator: PropTypes.func,
}

export default HiddenField
