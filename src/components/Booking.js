import classnames from 'classnames'
import get from 'lodash.get'
import moment from 'moment'
import 'moment-locale-fr'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { SingleDatePicker } from 'react-dates'

import VersoWrapper from './VersoWrapper'
import Price from './Price'
import Icon from './layout/Icon'
import Capitalize from './utils/Capitalize'
import { requestData } from '../reducers/data'
import { closeModal } from '../reducers/modal'
import selectBooking from '../selectors/booking'
import selectCurrentOffer from '../selectors/currentOffer'
import selectCurrentOfferer from '../selectors/currentOfferer'
import selectCurrentRecommendation from '../selectors/currentRecommendation'

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

  makeBooking = () => {
    const { offer, recommendation, requestData } = this.props
    this.setState({
      bookingInProgress: true,
    })
    requestData('POST', 'bookings', {
      add: 'append',
      body: {
        recommendationId: recommendation.id,
        offerId: offer.id,
        quantity: 1,
      },
    })
  }

  currentStep() {
    const token = get(this.props, 'booking.token')
    if (this.props.error) return 'error'
    if (token) return 'confirmation'
    if (this.state.bookingInProgress) return 'loading'
    return 'confirm'
  }

  getAvailableDateTimes(selectedDate) {
    const availableDates = get(
      this.props,
      'recommendation.mediatedOccurences',
      []
    ).map(o => moment(o.beginningDatetime))
    const availableHours = availableDates.filter(d =>
      d.isSame(selectedDate || this.state.date, 'day')
    )
    return {
      availableDates,
      availableHours,
    }
  }

  handleDateSelect = date => {
    const { availableHours } = this.getAvailableDateTimes(date)
    this.setState({
      date: date,
      time: availableHours[0],
    })
  }

  render() {
    const token = get(this.props, 'booking.token')
    const price = get(this.props, 'offer.price')
    const error = this.props.error
    const step = this.currentStep()
    const dateRequired =
      get(this.props, 'recommendation.mediatedOccurences', []).length > 1
    const dateOk = dateRequired ? this.state.date && this.state.time : true
    const offerer = this.props.offerer
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
                      initialVisibleMonth={() => moment.min(availableDates)}
                      inputIconPosition="after"
                      anchorDirection="center"
                      isDayBlocked={date =>
                        !availableDates.find(d => d.isSame(date, 'day'))
                      }
                      customInputIcon={<Icon svg="ico-calendar" />}
                      // customArrowIcon={<Icon svg='ico-next' />} // need in black
                      // customCloseIcon={<Icon svg='ico-close' />} // need in black
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
                      disabled={!this.state.date}
                    >
                      {availableHours.length === 0 && <option>hh:mm</option>}
                      {availableHours.map(d => (
                        <option key={d} value={moment(d).format('H:mm')}>
                          {moment(d).format('H:mm')}
                        </option>
                      ))}
                    </select>
                    <label htmlFor="time">
                      <Icon svg="ico-hour-list" className="input-icon" />
                    </label>
                  </div>
                </div>
              )}
              {dateOk && (
                <div>
                  {Boolean(offerer) ? (
                    <div>
                      <p>
                        Cette réservation d'une valeur de{' '}
                        <Price value={price} /> vous est offerte par :<br />
                        <strong>{offerer}</strong>.
                      </p>
                      <p>Nous comptons sur vous pour en profiter !</p>
                    </div>
                  ) : (
                    <div>
                      {price > 0 ? (
                        <div>
                          <p>
                            Vous êtes sur le point de réserver cette offre{price >
                              0 && (
                              <span>
                                {' '}
                                pour <Price value={price} />{' '}
                              </span>
                            )}.
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
            <div className="section success">
              <Icon className="mb2" svg="picto-validation" />
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
            <div className="section success">
              <p>Une erreur est survenue lors de la réservation :</p>
              {error && <p><Capitalize>{error}</Capitalize></p>}
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
                  onClick={this.makeBooking}
                >
                  Valider
                </button>
              </li>,
              <li key="cancel">
                <button
                  className="button is-secondary"
                  onClick={e => this.props.closeModal()}
                >
                  Annuler
                </button>
              </li>,
            ]}
            {step === 'loading' && (
              <li className="center">
                <Icon svg="loader-w" />
              </li>
            )}
            {step === 'confirmation' && (
              <li>
                <button
                  className="button is-secondary"
                  onClick={e => this.props.closeModal()}
                >
                  OK
                </button>
              </li>
            )}
            {step === 'error' && (
              <li>
                <button
                  className="button is-secondary"
                  onClick={e => this.props.closeModal()}
                >
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

export default connect(
  state => ({
    booking: selectBooking(state),
    offer: selectCurrentOffer(state),
    offerer: selectCurrentOfferer(state),
    recommendation: selectCurrentRecommendation(state),
    error: get(state, 'data.errors.global'),
  }),
  {
    requestData,
    closeModal,
  }
)(Booking)
