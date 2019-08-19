import { parseHoursByStockId } from '../../utils'
import { Field, FormSpy } from 'react-final-form'
import { SelectField } from '../../../../forms/inputs'
import React, { Fragment } from 'react'
import PropTypes from 'prop-types'
import classnames from 'classnames'
import BookingDatePickerField from './BookingDatePickerField/BookingDatePickerField'

// https://github.com/final-form/final-form#formstate
const spySubscriptions = {
  dirty: true,
  errors: true,
  initialValues: true,
  invalid: true,
  pristine: true,
  values: true,
}

const BookingFormContent = ({
                              className,
                              formId,
                              handleOnChange,
                              isEvent,
                              isReadOnly,
                              onMutation
                            }) => (formParams) => {
  const { handleSubmit, values } = formParams
  const { price } = values
  const bookableDates = parseHoursByStockId(values)
  const hasOneBookableDate = bookableDates.length === 1
  const hourLabel = hasOneBookableDate ? '' : 'Choisissez une heure'

  return (
    <Fragment>
      <FormSpy
        onChange={onMutation}
        subscription={spySubscriptions}
      />
      <form
        className={classnames(className, {
            'is-read-only': isReadOnly
          }
        )}
        id={formId}
        onSubmit={handleSubmit}
      >
        {isEvent && (
          <Fragment>
            <Field
              name="date"
              render={BookingDatePickerField(handleOnChange, values)}
            />
            {bookableDates && (
              <SelectField
                className="text-center"
                id="booking-form-time-picker-field"
                label={hourLabel}
                name="time"
                placeholder="Heure et prix"
                provider={bookableDates}
                readOnly={hasOneBookableDate}
              />
            )}
          </Fragment>
        )}

        {!isEvent && (
          <p className="text-center fs22">
            <span className="is-block">{'Vous êtes sur le point de réserver'}</span>
            <span className="is-block">{`cette offre pour ${price} €.`}</span>
          </p>
        )}
      </form>
    </Fragment>
  )
}

BookingFormContent.defaultProps = {
  className: '',
  isEvent: false,
  isReadOnly: false,
}

BookingFormContent.propTypes = {
  className: PropTypes.string,
  formId: PropTypes.string.isRequired,
  formParams: PropTypes.shape({
    handleSubmit: PropTypes.func.isRequired,
    values: PropTypes.shape().isRequired
  }).isRequired,
  isEvent: PropTypes.bool,
  isReadOnly: PropTypes.bool,
  onMutation: PropTypes.func.isRequired,
}

export default BookingFormContent
