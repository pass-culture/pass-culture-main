import React from 'react'
import { Form } from 'antd'
import PropTypes from 'prop-types'
// import arrayMutators from 'final-form-arrays'
import { Form as FinalForm, FormSpy } from 'react-final-form'

import { pipe } from '../../utils/functionnals'

// complete list of subscriptions
// https://github.com/final-form/final-form#formstate
const spySubscriptions = { pristine: true }
const defaultValidator = values => ({ errors: {}, values })

const withForm = (WrappedComponent, validator, calculator) => {
  class EditForm extends React.PureComponent {
    render() {
      const {
        id,
        children,
        onSubmit,
        className,
        onMutation,
        onValidation,
        onCalculation,
        initialValues,
        ...rest
      } = this.props
      return (
        <FinalForm
          validate={pipe(
            validator || defaultValidator,
            onValidation
          )}
          calculator={pipe(
            calculator,
            onCalculation
          )}
          onSubmit={onSubmit}
          // FIXME -> [DEPRECATED] Use form.mutators instead
          // mutators={{ ...arrayMutators }}
          initialValues={initialValues || {}}
          render={({ form, handleSubmit }) => (
            <React.Fragment>
              <FormSpy subscription={spySubscriptions} onChange={onMutation} />
              <Form
                id={id}
                layout="vertical"
                className={className}
                onSubmit={handleSubmit}
              >
                <WrappedComponent
                  {...rest}
                  form={form}
                  provider={initialValues}
                  onSubmit={() => form.submit()}
                  onReset={() => form.reset(initialValues)}
                >
                  {children}
                </WrappedComponent>
              </Form>
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
    onCalculation: null,
    onMutation: null,
    onValidation: null,
  }

  EditForm.propTypes = {
    children: PropTypes.node,
    className: PropTypes.string,
    id: PropTypes.string.isRequired,
    initialValues: PropTypes.object,
    onCalculation: PropTypes.func,
    onMutation: PropTypes.func,
    onSubmit: PropTypes.func.isRequired,
    onValidation: PropTypes.func,
  }

  return EditForm
}

export default withForm
