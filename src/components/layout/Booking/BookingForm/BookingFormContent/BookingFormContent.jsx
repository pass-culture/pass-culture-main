import { getCalendarProvider, parseHoursByStockId } from '../../utils'
import { Field, FormSpy } from 'react-final-form'
import { DatePickerField, SelectField } from '../../../../forms/inputs'
import React, { Fragment } from 'react'
import moment from 'moment'
import PropTypes from 'prop-types'
import classnames from 'classnames'

// https://github.com/final-form/final-form#formstate
const spySubscriptions = {
  dirty: true,
  errors: true,
  initialValues: true,
  invalid: true,
  pristine: true,
  values: true,
}

const renderDatePickerField = (handleOnChange, values) => ({ input }) => {
  const calendarDates = getCalendarProvider(values)
  const calendarLabel = calendarDates.length === 1 ? '' : 'Choisissez une date'
  const selectedValue = (input.value && input.value.date) || null
  const dateFormat = 'DD MMMM YYYY'

  return (
    <DatePickerField
      className="text-center mb36"
      dateFormat={dateFormat}
      hideToday
      id="booking-form-date-picker-field"
      label={calendarLabel}
      name="date"
      onChange={handleOnChange(input)}
      placeholder={moment().format(dateFormat)}
      popperPlacement="bottom"
      provider={calendarDates}
      readOnly={calendarDates.length === 1}
      selected={selectedValue}
    />
  )
}

const BookingFormContent = ({ handleOnChange, props }) => ({ handleSubmit, values }) => {
  const { className, formId, isEvent, isReadOnly, onMutation } = props
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
              render={renderDatePickerField(handleOnChange, values)}
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
  isEvent: PropTypes.bool,
  isReadOnly: PropTypes.bool,
  onMutation: PropTypes.func.isRequired,
}

export default BookingFormContent
