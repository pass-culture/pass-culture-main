import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { Form } from 'react-final-form'
import decorators from './decorators/decorators'
import BookingFormContent from './BookingFormContent/BookingFormContent'

class BookingForm extends Component {
  handleOnChange = (input) => (date, event) => {
    input.onChange({ date })
    event.preventDefault()
  }

  render() {
    const { className, formId, initialValues, isEvent, isReadOnly, onMutation, onSubmit} = this.props

    return (
      <Form
        decorators={decorators}
        initialValues={initialValues}
        onSubmit={onSubmit}
        render={BookingFormContent({
          className,
          formId,
          handleOnChange: this.handleOnChange,
          isEvent,
          isReadOnly,
          onMutation
        })}
      />
    )
  }
}

BookingForm.defaultProps = {
  className: '',
  initialValues: null,
  isEvent: false,
  isReadOnly: false,
}

BookingForm.propTypes = {
  className: PropTypes.string,
  formId: PropTypes.string.isRequired,
  initialValues: PropTypes.shape(),
  isEvent: PropTypes.bool,
  isReadOnly: PropTypes.bool,
  onMutation: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
}

export default BookingForm
