import classnames from 'classnames'
import get from 'lodash.get'
import moment from 'moment'
import 'moment-locale-fr'
import {
  capitalize,
  closeModal,
  Icon,
  removeDataError,
  requestData,
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { SingleDatePicker } from 'react-dates'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Price from './Price'
import VersoWrapper from './VersoWrapper'
import bookingSelector from '../selectors/booking'
import currentOfferSelector from '../selectors/currentOffer'
import currentRecommendationSelector from '../selectors/currentRecommendation'
import timezoneSelector from '../selectors/currentTimezone'
moment.locale('fr')

class Booking extends Component {
  constructor() {
    super()
    this.state = {
      bookingInProgress: false,
      date: null,
      time: null,
      focused: false,
    }
  }

  closeBooking = () => {
    this.props.removeDataError()
    this.props.closeModal()
  }

  currentStep = () => {
    const {
      booking,
      error
    } = this.props
    const {
      token
    } = (booking || {})
    const { bookingInProgress  } = this.state

    if (error) return 'error'
    if (token) return 'confirmation'
    if (bookingInProgress) return 'loading'
    return 'confirm'
  }

  getAvailableDateTimes = (selectedDate) => {
    const mediatedOccurences = get(
      this.props,
      'currentRecommendation.mediatedOccurences',
      []
    )
    const { tz } = this.props
    const NOW = moment()
    const availableDates = mediatedOccurences
      .filter(o => moment(o.offer[0].bookingLimitDatetime).isAfter(NOW))
      .map(o => moment(o.beginningDatetime).tz(tz))
    const availableMediatedOccurences = []
    const availableHours = availableDates.filter((d, index) => {
      const isFiltered = d.isSame(selectedDate || this.state.date, 'day')
      if (isFiltered) {
        availableMediatedOccurences.push(mediatedOccurences[index])
      }
      return isFiltered
    })
    return {
      availableDates,
      availableHours,
      availableMediatedOccurences,
    }
  }

  handleDateSelect = date => {
    const {
      availableMediatedOccurences,
      availableHours,
    } = this.getAvailableDateTimes(date)
    this.setState({
      date: date,
      occurences: availableMediatedOccurences,
      time: availableHours[0],
    })
  }

  makeBooking = event => {
    const { currentRecommendation,
      // offer,
      requestData
    } = this.props
    const {
      offer
    } = (currentRecommendation || {})
    const { occurences } = this.state
    this.setState({
      bookingInProgress: true,
    })
    const selectedOffer =
      occurences &&
      occurences[0] &&
      occurences[0].offer &&
      occurences[0].offer[0]
    const offerId = selectedOffer ? selectedOffer.id : offer.id
    requestData('POST', 'bookings', {
      add: 'append',
      body: {
        currentRecommendationId: currentRecommendation.id,
        offerId,
        quantity: 1,
      },
    })
  }

  render() {
    const {
      booking,
      currentRecommendation,
      error,
      tz
    } = this.props
    const {
      token
    } = (booking || {})
    const {
      offer
    } = (currentRecommendation || {})
    const {
      price,
      venue
    } = (offer || {})
    const {
      managingOfferer
    } = (venue || {})

    const step = this.currentStep()
    const dateRequired =
      get(this.props, 'currentRecommendation.mediatedOccurences', []).length > 1
    const dateOk = dateRequired ? this.state.date && this.state.time : true
    const { availableDates, availableHours } = this.getAvailableDateTimes()
    return (
      <VersoWrapper>
        <div className="booking">
          {step === 'confirm' && (
            <div>
              {dateRequired && (
                <div>
                  <label htmlFor="date">
                    <h6>Choisissez une date :</h6>
                  </label>
                  <div className="input-field date-picker">
                    <SingleDatePicker
                      date={this.state.date}
                      onDateChange={this.handleDateSelect}
                      focused={this.state.focused}
                      onFocusChange={({ focused }) =>
                        this.setState({ focused })
                      }
                      numberOfMonths={1}
                      noBorder={true}
                      initialVisibleMonth={() =>
                        moment.min(availableDates.filter(d => d > moment.now()))
                      }
                      inputIconPosition="after"
                      anchorDirection="center"
                      isDayBlocked={date =>
                        !availableDates.find(d => d.isSame(date.tz(tz), 'day'))
                      }
                      customInputIcon={
                        <Icon svg="ico-calendar" alt="calendrier" />
                      }
                      customCloseIcon={<Icon svg="ico-close-b" alt="Fermer" />}
                      displayFormat="LL"
                    />
                  </div>
                  <label htmlFor="time">
                    <h6>Choisissez une heure :</h6>
                  </label>
                  <div className="input-field" htmlFor="time">
                    <select
                      id="time"
                      value={this.state.time || ''}
                      className="input"
                      onChange={e => this.setState({ time: e.target.value })}
                      disabled={!this.state.date}>
                      {availableHours.length === 0 && <option>hh:mm</option>}
                      {availableHours.map(d => (
                        <option
                          key={d}
                          value={moment(d)
                            .tz(tz)
                            .format('H:mm')}>
                          {moment(d)
                            .tz(tz)
                            .format('H:mm')}
                        </option>
                      ))}
                    </select>
                    <label htmlFor="time">
                      <Icon
                        svg="ico-hour-list"
                        className="input-icon"
                        alt="Horaires"
                      />
                    </label>
                  </div>
                </div>
              )}
              {dateOk && (
                <div>
                  {managingOfferer ? (
                    <div>
                      <p>
                        Cette réservation d'une valeur de{' '}
                        <Price value={price} /> vous est offerte par :<br />
                        <strong>{managingOfferer.name}</strong>.
                      </p>
                      <p>Nous comptons sur vous pour en profiter !</p>
                    </div>
                  ) : (
                    <div>
                      {price > 0 ? (
                        <div>
                          <p>
                            Vous êtes sur le point de réserver cette offre
                            {price > 0 && (
                              <span>
                                {' '}
                                pour <Price value={price} />{' '}
                              </span>
                            )}
                            .
                          </p>
                          <p>
                            <small>
                              Le montant sera déduit de votre pass. Il vous
                              restera <Price value={0} free="——€" /> après cette
                              réservation.
                            </small>
                          </p>
                        </div>
                      ) : (
                        <div>
                          <p>
                            Vous êtes sur le point de réserver cette offre
                            gratuite.
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
          {step === 'loading' && <p>Réservation en cours ...</p>}
          {step === 'confirmation' && (
            <div className="section finished">
              <Icon svg="picto-validation" alt="Réservation validée" />
              <p>Votre réservation est validée.</p>
              <p>
                {price > 0 && (
                  <small>
                    <Price value={price} /> ont été déduits de votre pass.
                  </small>
                )}
                <br />
                <small>Présentez le code suivant sur place :</small>
              </p>
              <p>
                <big>{token}</big>
              </p>
              <p>
                <small>
                  Retrouvez ce code et les détails de l'offre dans la rubrique
                  "Mes réservations" de votre compte.
                </small>
              </p>
            </div>
          )}
          {step === 'error' && (
            <div className="section finished">
              <Icon svg="picto-echec" alt="Echec de réservation" />
              <p>Une erreur est survenue lors de la réservation :</p>
              {error && (
                <p>
                  {capitalize(
                    Object.values(error)
                      .map(messages => messages.join(';'))
                      .join(';'))
                  }
                </p>
              )}
            </div>
          )}
          <ul className="bottom-bar">
            {step === 'confirm' && [
              <li key="submit">
                <button
                  className={classnames({
                    button: true,
                    'is-primary': true,
                    'is-hidden': !dateOk,
                  })}
                  onClick={this.makeBooking}>
                  Valider
                </button>
              </li>,
              <li key="cancel">
                <button
                  className="button is-secondary"
                  onClick={this.closeBooking}>
                  Annuler
                </button>
              </li>,
            ]}
            {step === 'loading' && (
              <li className="center">
                <Icon svg="loader-w" alt="Chargement ..." />
              </li>
            )}
            {step === 'confirmation' && (
              <li>
                <button
                  className="button is-secondary"
                  onClick={this.closeBooking}>
                  OK
                </button>
              </li>
            )}
            {step === 'error' && (
              <li>
                <button
                  className="button is-secondary"
                  onClick={this.closeBooking}>
                  Retour
                </button>
              </li>
            )}
          </ul>
        </div>
      </VersoWrapper>
    )
  }
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const { mediationId, offerId } = ownProps.match.params
      return {
        booking: bookingSelector(state),
        currentRecommendation: currentRecommendationSelector(state, offerId, mediationId),
        error: get(state.data, 'errors'),
        offer: currentOfferSelector(state),
        tz: timezoneSelector(state),
      }
    },
    { closeModal, removeDataError, requestData }
  )
)(Booking)
