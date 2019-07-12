import React, { Component, Fragment } from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import FormError from '../FormError'
import { isEmpty } from '../../../utils/strings'

const DEFAULT_REQUIRED_ERROR = 'Ce champ est requis'
const validateRequiredField = value => {
  if (value && !isEmpty(value)) return undefined
  return DEFAULT_REQUIRED_ERROR
}

class CheckBoxField extends Component {
  renderField = ({ input, meta }) => {
    const { children, className, required } = this.props

    return (
      <Fragment>
        <p className={className}>
          <span className={className}>
            <input
              {...input}
              className="input no-background"
              required={!!required}
              type="checkbox"
            />
            {children}
          </span>
        </p>
        <FormError meta={meta} />
      </Fragment>
    )
  }

  render() {
    const { name, required } = this.props
    const validateFunc =
      required && typeof required === 'function'
        ? required
        : (required && validateRequiredField) || undefined

    return (
      <Field
        name={name}
        render={this.renderField}
        type="checkbox"
        validate={validateFunc || undefined}
      />
    )
  }
}

CheckBoxField.defaultProps = {
  className: null,
  required: false,
}

CheckBoxField.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
  name: PropTypes.string.isRequired,
  required: PropTypes.oneOfType([PropTypes.bool, PropTypes.func]),
}

export default CheckBoxField
