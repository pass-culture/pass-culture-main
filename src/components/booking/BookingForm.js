/* eslint
  react/jsx-one-expression-per-line: 0 */
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
} from './utils'
import { DatePickerField, HiddenField, SelectField } from '../forms/inputs'

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
  formId,
  disabled,
  initialValues,
  onMutation,
  onSubmit,
}) => (
  <FinalForm
    validate={null}
    onSubmit={onSubmit}
    decorators={decorators}
    initialValues={initialValues || {}}
    render={({ form, values, handleSubmit }) => {
      const { stockId, price } = values
      const calendarDates = getCalendarProvider(values)
      const hoursAndPrices = parseHoursByStockId(values)
      //
      const hourReadOnly = hoursAndPrices.length === 1
      const hourLabel = hourReadOnly ? false : 'Choisissez une heure'

      const calendarReadOnly = calendarDates.length === 1
      const calendarLabel = calendarReadOnly ? false : 'Choisissez une date'
      return (
        <React.Fragment>
          <FormSpy onChange={onMutation} subscription={spySubscriptions} />
          <form
            id={formId}
            disabled={disabled}
            className={className}
            onSubmit={handleSubmit}
          >
            <HiddenField name="price" />
            <HiddenField name="stockId" />
            {isEvent && (
              <React.Fragment>
                <Field
                  name="date"
                  render={({ input }) => {
                    const selectedValue =
                      (input.value && input.value.date) || null
                    const dateFormat = 'DD MMMM YYYY'
                    return (
                      <DatePickerField
                        hideToday
                        name="date"
                        label={calendarLabel}
                        readOnly={calendarReadOnly}
                        className="text-center mb36"
                        selected={selectedValue}
                        provider={calendarDates}
                        dateFormat={dateFormat}
                        popperPlacement="bottom"
                        popperRefContainer={datepickerPopper}
                        placeholder={moment().format(dateFormat)}
                        onChange={date => {
                          // legacy ancien calendrier
                          input.onChange({ date })
                        }}
                      />
                    )
                  }}
                />
                <div id="datepicker-popper-container" ref={datepickerPopper} />
                {hoursAndPrices && (
                  <SelectField
                    name="time"
                    readOnly={hourReadOnly}
                    provider={hoursAndPrices}
                    placeholder="Heure et prix"
                    label={hourLabel}
                    className="text-center"
                  />
                )}
              </React.Fragment>
            )}
            {stockId && (
              <p className="text-center fs22">
                <span className="is-block">
                  Vous êtes sur le point de réserver
                </span>
                <span className="is-block">cette offre pour {price}€</span>
              </p>
            )}
          </form>
        </React.Fragment>
      )
    }}
  />
)

BookingForm.defaultProps = {
  className: '',
  initialValues: null,
  isEvent: false,
}

BookingForm.propTypes = {
  className: PropTypes.string,
  disabled: PropTypes.bool.isRequired,
  formId: PropTypes.string.isRequired,
  initialValues: PropTypes.object,
  isEvent: PropTypes.bool,
  onMutation: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
}

export default BookingForm
