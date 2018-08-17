import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

export const HiddenField = ({ name }) => (
  <Field name={name} type="hidden" component="input" />
)

HiddenField.propTypes = {
  name: PropTypes.string.isRequired,
}

export default HiddenField
