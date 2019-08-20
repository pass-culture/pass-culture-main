import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { Form } from 'react-final-form'

import BookingFormContent from './BookingFormContent/BookingFormContent'
import decorators from './decorators/decorators'

class BookingForm extends Component {
  renderBookingFormContent = formParams => {
    const { className, formId, isEvent, isReadOnly, onSetCanSubmitForm } = this.props
    return (
      <BookingFormContent
        className={className}
        formId={formId}
        isEvent={isEvent}
        isReadOnly={isReadOnly}
        onSetCanSubmitForm={onSetCanSubmitForm}
        {...formParams}
      />
    )
  }

  render() {
    const { initialValues, onFormSubmit } = this.props
    return (
      <Form
        decorators={decorators}
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
