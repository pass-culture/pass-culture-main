/* eslint
    react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'
import { Form } from 'react-final-form'

import { canSubmitForm } from '../utils'

const FormWrapper = ({
  children,
  className,
  initialValues,
  isLoading,
  onFormSubmit,
}) => (
  <Form
    onSubmit={onFormSubmit}
    initialValues={initialValues}
    render={formProps => {
      const formValues = formProps.values || {}
      const canSubmit = !isLoading && canSubmitForm(formProps)
      const formErrors = !formProps.pristine && formProps.error
      return (
        <form
          noValidate
          autoComplete="off"
          disabled={isLoading}
          onSubmit={formProps.handleSubmit}
          className={className}
        >
          {children(canSubmit, formValues, formErrors)}
        </form>
      )
    }}
  />
)

FormWrapper.propTypes = {
  children: PropTypes.func.isRequired,
  className: PropTypes.string.isRequired,
  initialValues: PropTypes.object.isRequired,
  isLoading: PropTypes.bool.isRequired,
  onFormSubmit: PropTypes.func.isRequired,
}

export default FormWrapper
