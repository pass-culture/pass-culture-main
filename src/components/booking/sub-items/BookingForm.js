import React from 'react'
import moment from 'moment'
import PropTypes from 'prop-types'
import createDecorator from 'final-form-calculate'
import { Field, Form as FinalForm, FormSpy } from 'react-final-form'

import {
  getCalendarProvider,
  parseHoursByStockId,
  onCalendarUpdates,
  onTimeUpdates,
} from '../utils'
import { DatePickerField, HiddenField, SelectField } from '../../forms/inputs'

const spySubscriptions = {
  // complete list of subscriptions
  // https://github.com/final-form/final-form#formstate
  dirty: true,
  errors: true,
  initialValues: true,
  invalid: true,
  pristine: true,
  values: true,
}

/* -------- form calculators --------  */
const decorators = [
  createDecorator(
    { field: 'date', updates: onCalendarUpdates },
    { field: 'time', updates: onTimeUpdates }
  ),
]

const datepickerPopper = React.createRef()

const BookingForm = ({
  className,
  isEvent,
  isReadOnly,
  formId,
  disabled,
  initialValues,
  onMutation,
  onSubmit,
}) => (
  <FinalForm
    decorators={decorators}
    initialValues={initialValues || {}}
    onSubmit={onSubmit}
    render={({ form, values, handleSubmit }) => {
      const { stockId, price } = values
      const calendarDates = getCalendarProvider(values)
      const hoursAndPrices = parseHoursByStockId(values)

      const hourReadOnly = hoursAndPrices.length === 1
      const hourLabel = hourReadOnly ? false : 'Choisissez une heure'

      const calendarReadOnly = calendarDates.length === 1
      const calendarLabel = calendarReadOnly ? false : 'Choisissez une date'

      const readOnlyClassname = isReadOnly ? 'is-read-only' : ''
      return (
        <React.Fragment>
          <FormSpy
            onChange={onMutation}
            subscription={spySubscriptions}
          />
          <form
            className={`${className} ${readOnlyClassname}`}
            disabled={disabled}
            id={formId}
            onSubmit={handleSubmit}
          >
            <HiddenField name="price" />
            <HiddenField name="stockId" />
            {isEvent && (
              <React.Fragment>
                <Field
                  name="date"
                  render={({ input }) => {
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
                        onChange={date => {
                          // legacy ancien calendrier
                          input.onChange({ date })
                        }}
                        placeholder={moment().format(dateFormat)}
                        popperPlacement="bottom"
                        popperRefContainer={datepickerPopper}
                        provider={calendarDates}
                        readOnly={calendarReadOnly}
                        selected={selectedValue}
                      />
                    )
                  }}
                />
                <div
                  id="datepicker-popper-container"
                  ref={datepickerPopper}
                />
                {hoursAndPrices && (
                  <SelectField
                    className="text-center"
                    id="booking-form-time-picker-field"
                    label={(typeof hourLabel === 'string' && hourLabel) || ''}
                    name="time"
                    placeholder="Heure et prix"
                    provider={hoursAndPrices}
                    readOnly={hourReadOnly}
                  />
                )}
              </React.Fragment>
            )}
            {stockId && (
              <p className="text-center fs22">
                <span className="is-block">{'Vous êtes sur le point de réserver'}</span>
                <span className="is-block">{`cette offre pour ${price}€`}</span>
              </p>
            )}
          </form>
        </React.Fragment>
      )
    }}
    validate={null}
  />
)

BookingForm.defaultProps = {
  className: '',
  initialValues: null,
  isEvent: false,
  isReadOnly: false,
}

BookingForm.propTypes = {
  className: PropTypes.string,
  disabled: PropTypes.bool.isRequired,
  formId: PropTypes.string.isRequired,
  initialValues: PropTypes.shape(),
  isEvent: PropTypes.bool,
  isReadOnly: PropTypes.bool,
  onMutation: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
}

export default BookingForm
