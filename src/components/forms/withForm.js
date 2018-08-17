import React from 'react'
import { Form } from 'antd'
import PropTypes from 'prop-types'
// import arrayMutators from 'final-form-arrays'
import { Form as FinalForm, FormSpy } from 'react-final-form'

// complete list of subscriptions
// https://github.com/final-form/final-form#formstate
const spySubscriptions = {
  errors: true,
  invalid: true,
  pristine: true,
  values: true,
}

// NOTE -> Validator
// github.com/final-form/react-final-form#synchronous-record-level-validation
// NOTE -> Calculator
// github.com/final-form/react-final-form#calculated-fields
const withForm = (WrappedComponent, validator, calculator) => {
  class EditForm extends React.PureComponent {
    render() {
      const {
        id,
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
          // FIXME -> [DEPRECATED] Use form.mutators instead
          // mutators={{ ...arrayMutators }}
          initialValues={initialValues}
          decorators={calculator && [calculator]}
          render={({ form, values, handleSubmit }) => (
            <React.Fragment>
              <Form
                id={id}
                layout="vertical"
                className={className}
                onSubmit={handleSubmit}
              >
                <WrappedComponent
                  {...rest}
                  form={form}
                  values={values}
                  provider={initialValues}
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
    initialValues: {},
    onMutation: null,
  }

  EditForm.propTypes = {
    children: PropTypes.node,
    className: PropTypes.string,
    id: PropTypes.string.isRequired,
    initialValues: PropTypes.object,
    onMutation: PropTypes.func,
    onSubmit: PropTypes.func.isRequired,
  }

  return EditForm
}

export default withForm
