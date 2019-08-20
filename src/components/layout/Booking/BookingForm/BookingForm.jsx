import PropTypes from 'prop-types'
import React, { Component } from 'react'
import { Form } from 'react-final-form'

import BookingFormContent from './BookingFormContent/BookingFormContent'
import decorators from './decorators/decorators'

class BookingForm extends Component {
  handleOnChange = input => (date, event) => {
    input.onChange({ date })
    event.preventDefault()
  }

  renderBookingFormContent = formParams => {
    const { className, formId, isEvent, isReadOnly, onMutation } = this.props
    const { handleSubmit, values } = formParams
    return (
      <BookingFormContent
        className={className}
        formId={formId}
        isEvent={isEvent}
        isReadOnly={isReadOnly}
        onChange={this.handleOnChange}
        onMutation={onMutation}
        onSubmit={handleSubmit}
        values={values}
      />
    )
  }

  render() {
    const { initialValues, onSubmit } = this.props

    return (
      <Form
        decorators={decorators}
        initialValues={initialValues}
        onSubmit={onSubmit}
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
  onMutation: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
}

export default BookingForm
