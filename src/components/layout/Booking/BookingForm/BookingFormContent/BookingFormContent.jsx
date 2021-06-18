import moment from 'moment'
import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'
import { Field } from 'react-final-form'

import formatDecimals from '../../../../../utils/numbers/formatDecimals'
import CheckBoxField from '../../../../forms/inputs/CheckBoxField'
import DatePickerField from '../../../../forms/inputs/DatePickerField/DatePickerField'
import SelectField from '../../../../forms/inputs/SelectField'
import DuoOfferContainer from '../../../../layout/DuoOffer/DuoOfferContainer'
import getCalendarProvider from '../../utils/getCalendarProvider'
import parseHoursByStockId from '../../utils/parseHoursByStockId'

class BookingFormContent extends PureComponent {
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
    const calendarLabel = calendarDates.length === 1 ? '' : 'Choisis une date :'
    const dateFormat = 'DD MMMM YYYY'

    return (
      <div className="booking-form-content-datepicker">
        <DatePickerField
          {...input}
          clearable={false}
          dateFormat={dateFormat}
          extraClassName="text-center mb36"
          hideToday
          id="booking-form-date-picker-field"
          includeDates={calendarDates}
          label={calendarLabel}
          name="date"
          onChange={this.handleChangeAndRemoveCalendar(input)}
          readOnly={calendarDates.length === 1}
          selected={value === '' ? null : value}
        />
      </div>
    )
  }

  renderIsDuo = () => {
    const { offerId } = this.props

    return (
      <DuoOfferContainer
        label="Réserver 2 places"
        offerId={offerId}
      />
    )
  }

  cancellation_limit_date_sentences = (bookableTimes, hasBookableTimes, isEvent) => {
    if (bookableTimes.length === 0) return null

    const cancellation_limit_date = moment(bookableTimes[0].cancellationLimitDate)
    const now = moment()
    let sentence = ''

    if (cancellation_limit_date.diff(now) < 0) {
      sentence = 'Cette réservation n’est pas annulable'
    } else if (bookableTimes && hasBookableTimes && isEvent) {
      sentence = `Réservation annulable jusqu’au ${cancellation_limit_date.format(
        'DD/MM/YYYY H:mm'
      )}`
    }

    return (
      <p className="bc-notification">
        {sentence}
      </p>
    )
  }

  render() {
    const {
      canExpire,
      extraClassName,
      formId,
      handleSubmit,
      isDigital,
      isEvent,
      isReadOnly,
      isStockDuo,
      autoActivateDigitalBookings,
      enableActivationCodes,
      hasActivationCode,
      values,
    } = this.props
    const { price, isDuo } = values
    const bookableTimes = parseHoursByStockId(values)
    const hasOneBookableTime = bookableTimes.length === 1
    const hasBookableTimes = bookableTimes.length > 0
    const hourLabel = hasOneBookableTime ? '' : 'Choisis une heure :'
    const displayPriceWarning = !isEvent || (bookableTimes && hasBookableTimes)
    const computedPrice = isDuo ? price * 2 : price
    const formattedComputedPrice = formatDecimals(computedPrice)

    return (
      <form
        className={`${extraClassName} ${isReadOnly ? 'is-read-only' : ''}`}
        id={formId}
        onSubmit={handleSubmit}
      >
        {isEvent && (
          <Fragment>
            <Field
              name="date"
              render={this.renderBookingDatePickerField}
            />
            {bookableTimes && hasBookableTimes && (
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
            {isStockDuo && (
              <div className="isDuo">
                <CheckBoxField
                  name="isDuo"
                  required={false}
                >
                  {this.renderIsDuo()}
                </CheckBoxField>
              </div>
            )}
          </Fragment>
        )}

        {displayPriceWarning && (
          <p className="text-center fs22">
            <span className="is-block">
              {'Tu es sur le point de réserver'}
            </span>
            <span className="is-block">
              {`cette offre pour ${formattedComputedPrice} €.`}
            </span>
          </p>
        )}

        {!isEvent && canExpire && isDigital && !autoActivateDigitalBookings && (
          <p className="bc-notification">
            {
              'Tu as 30 jours pour faire valider ta contremarque. Passé ce délai, ta réservation sera automatiquement annulée.'
            }
          </p>
        )}

        {!isEvent &&
          canExpire &&
          isDigital &&
          hasActivationCode &&
          autoActivateDigitalBookings &&
          enableActivationCodes && (
            <p className="bc-notification">
              {
                "Pour cette offre numérique, ta réservation sera définitivement validée. Tu ne pourras pas l'annuler par la suite."
              }
            </p>
        )}

        {!isEvent && canExpire && !isDigital && (
          <p className="bc-notification">
            {
              'Tu as 30 jours pour récupérer ton bien et faire valider ta contremarque. Passé ce délai, ta réservation sera automatiquement annulée.'
            }
          </p>
        )}

        {this.cancellation_limit_date_sentences(bookableTimes, hasBookableTimes, isEvent)}
      </form>
    )
  }
}

BookingFormContent.defaultProps = {
  extraClassName: '',
  isEvent: false,
  isReadOnly: false,
  isStockDuo: false,
  offerId: '',
}

BookingFormContent.propTypes = {
  autoActivateDigitalBookings: PropTypes.bool.isRequired,
  canExpire: PropTypes.bool.isRequired,
  enableActivationCodes: PropTypes.bool.isRequired,
  extraClassName: PropTypes.string,
  formId: PropTypes.string.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  hasActivationCode: PropTypes.bool.isRequired,
  invalid: PropTypes.bool.isRequired,
  isDigital: PropTypes.bool.isRequired,
  isEvent: PropTypes.bool,
  isReadOnly: PropTypes.bool,
  isStockDuo: PropTypes.bool,
  offerId: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  values: PropTypes.shape().isRequired,
}

export default BookingFormContent
