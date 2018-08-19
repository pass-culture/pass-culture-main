import React from 'react'
import { Form } from 'antd'
import PropTypes from 'prop-types'
import createDecorator from 'final-form-calculate'
// import arrayMutators from 'final-form-arrays'
import { Form as FinalForm, FormSpy } from 'react-final-form'

// React Final Form Validator
// github.com/final-form/react-final-form#synchronous-record-level-validation
const withForm = (WrappedComponent, validator, calculator) => {
  const decorators = [
    // React Final Form Calculator
    // github.com/final-form/react-final-form#calculated-fields
    // FIXME -> console.error lors du hot reload
    // https://github.com/final-form/react-final-form/issues/270
    calculator && createDecorator(...calculator),
  ]

  const spySubscriptions = {
    // complete list of subscriptions
    // https://github.com/final-form/final-form#formstate
    errors: true,
    invalid: true,
    pristine: true,
    values: true,
  }

  class EditForm extends React.PureComponent {
    render() {
      const {
        formId,
        children,
        onSubmit,
        className,
        onMutation,
        initialValues,
        ...rest
      } = this.props
      return (
        <FinalForm
          onSubmit={onSubmit}
          validate={validator}
          decorators={decorators}
          // FIXME -> [DEPRECATED] Use form.mutators instead
          // mutators={{ ...arrayMutators }}
          initialValues={initialValues || {}}
          render={({ form, values, handleSubmit }) => (
            <React.Fragment>
              <Form
                id={formId}
                layout="vertical"
                className={className}
                onSubmit={handleSubmit}
              >
                <WrappedComponent
                  {...rest}
                  form={form}
                  formValues={values}
                  onSubmit={() => form.submit()}
                  onReset={() => form.reset(initialValues)}
                >
                  {children}
                </WrappedComponent>
              </Form>
              <FormSpy onChange={onMutation} subscription={spySubscriptions} />
            </React.Fragment>
          )}
        />
      )
    }
  }

  EditForm.defaultProps = {
    children: null,
    className: null,
    initialValues: null,
    onMutation: null,
  }

  EditForm.propTypes = {
    children: PropTypes.node,
    className: PropTypes.string,
    formId: PropTypes.string.isRequired,
    initialValues: PropTypes.object,
    onMutation: PropTypes.func,
    onSubmit: PropTypes.func.isRequired,
  }

  return EditForm
}

export default withForm
