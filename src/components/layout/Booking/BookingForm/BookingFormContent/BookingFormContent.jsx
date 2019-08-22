import classnames from 'classnames'
import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import { Field } from 'react-final-form'

import { getCalendarProvider, parseHoursByStockId } from '../../utils'
import SelectField from '../../../../forms/inputs/SelectField'
import DatePickerField from '../../../../forms/inputs/DatePickerField/DatePickerField'

class BookingFormContent extends Component {
  componentDidMount() {
    const { invalid, onChange, values } = this.props
    const { price, stockId } = values
    if (stockId) {
      const nextCanSubmitForm = Boolean(!invalid && stockId && price >= 0)
      onChange(nextCanSubmitForm)
    }
  }

  componentDidUpdate(prevProps) {
    const { invalid, onChange, values } = this.props
    const { price, stockId } = values
    if (stockId !== prevProps.values.stockId) {
      const nextCanSubmitForm = Boolean(!invalid && stockId && price >= 0)
      onChange(nextCanSubmitForm)
    }
  }

  handleChangeAndRemoveCalendar = input => (value, event) => {
    event.preventDefault()
    input.onChange(value)
  }

  renderBookingDatePickerField = ({ input }) => {
    const { values } = this.props
    const { value } = input
    const calendarDates = getCalendarProvider(values)
    const calendarLabel = calendarDates.length === 1 ? '' : 'Choisissez une date'
    const dateFormat = 'DD MMMM YYYY'
    return (
      <DatePickerField
        {...input}
        className="text-center mb36"
        clearable={false}
        dateFormat={dateFormat}
        hideToday
        id="booking-form-date-picker-field"
        includeDates={calendarDates}
        label={calendarLabel}
        name="date"
        onChange={this.handleChangeAndRemoveCalendar(input)}
        popperPlacement="bottom"
        readOnly={calendarDates.length === 1}
        selected={value}
      />
    )
  }

  render() {
    const { className, formId, handleSubmit, isEvent, isReadOnly, values } = this.props
    const { price } = values
    const bookableTimes = parseHoursByStockId(values)
    const hasOneBookableTime = bookableTimes.length === 1
    const hourLabel = hasOneBookableTime ? '' : 'Choisissez une heure'
    return (
      <form
        className={classnames(className, {
          'is-read-only': isReadOnly,
        })}
        id={formId}
        onSubmit={handleSubmit}
      >
        {isEvent && (
          <Fragment>
            <Field
              name="date"
              render={this.renderBookingDatePickerField}
            />
            {bookableTimes && (
              <SelectField
                className="text-center"
                id="booking-form-time-picker-field"
                label={hourLabel}
                name="time"
                options={bookableTimes}
                placeholder="Heure et prix"
                readOnly={hasOneBookableTime}
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
    )
  }
}

BookingFormContent.defaultProps = {
  className: '',
  isEvent: false,
  isReadOnly: false,
}

BookingFormContent.propTypes = {
  className: PropTypes.string,
  formId: PropTypes.string.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  invalid: PropTypes.bool.isRequired,
  isEvent: PropTypes.bool,
  isReadOnly: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
  values: PropTypes.shape().isRequired,
}

export default BookingFormContent
