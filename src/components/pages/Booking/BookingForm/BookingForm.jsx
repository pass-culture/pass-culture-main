import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { Form } from 'react-final-form'

import BookingFormContent from './BookingFormContent/BookingFormContent'
import eventDecorators from './decorators/eventDecorators'

class BookingForm extends Component {
  renderBookingFormContent = formParams => {
    const { className, formId, isEvent, isReadOnly, onSetCanSubmitForm } = this.props
    const { handleSubmit, invalid, values } = formParams

    return (
      <BookingFormContent
        className={className}
        formId={formId}
        handleSubmit={handleSubmit}
        invalid={invalid}
        isEvent={isEvent}
        isReadOnly={isReadOnly}
        onChange={onSetCanSubmitForm}
        values={values}
      />
    )
  }

  render() {
    const { initialValues, isEvent, onFormSubmit } = this.props

    return (
      <Form
        decorators={isEvent && eventDecorators}
        initialValues={initialValues}
        onSubmit={onFormSubmit}
        render={this.renderBookingFormContent}
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
  onFormSubmit: PropTypes.func.isRequired,
  onSetCanSubmitForm: PropTypes.func.isRequired,
}

export default BookingForm
