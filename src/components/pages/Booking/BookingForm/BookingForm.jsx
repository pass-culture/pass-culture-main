import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { Form } from 'react-final-form'

import BookingFormContentContainer from './BookingFormContent/BookingFormContentContainer'
import eventDecorators from './decorators/eventDecorators'

class BookingForm extends Component {
  renderBookingFormContent = formParams => {
    const { className, formId, isEvent, isReadOnly, offerId, onSetCanSubmitForm } = this.props
    const { handleSubmit, invalid, values } = formParams

    return (
      <BookingFormContentContainer
        className={className}
        formId={formId}
        handleSubmit={handleSubmit}
        invalid={invalid}
        isEvent={isEvent}
        isReadOnly={isReadOnly}
        offerId={offerId}
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
  offerId: '',
}

BookingForm.propTypes = {
  className: PropTypes.string,
  formId: PropTypes.string.isRequired,
  initialValues: PropTypes.shape(),
  isEvent: PropTypes.bool,
  isReadOnly: PropTypes.bool,
  offerId: PropTypes.string,
  onFormSubmit: PropTypes.func.isRequired,
  onSetCanSubmitForm: PropTypes.func.isRequired,
}

export default BookingForm
