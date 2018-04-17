import React, { Component } from 'react'
import { connect } from 'react-redux'
import get from 'lodash.get';
import classnames from 'classnames';
import moment from 'moment'

import Icon from '../components/Icon'
import Price from '../components/Price'
import VersoWrapper from '../components/VersoWrapper'
import { requestData } from '../reducers/data'
import { closeModal } from '../reducers/modal'
import selectBooking from '../selectors/booking'
import selectOffer from '../selectors/offer'
import selectUserMediation from '../selectors/userMediation'

class Booking extends Component {
  constructor () {
    super()
    this.state = {
      bookingInProgress: false,
      date: null,
      time: null,
    }
  }

  makeBooking = () => {
    const { offer, userMediation, requestData } = this.props
    this.setState({
      bookingInProgress: true
    })
    requestData('POST', 'bookings', {
      add: 'append',
      body: {
        userMediationId: userMediation.id,
        offerId: offer.id,
        quantity: 1,
      }
    })
  }

  currentStep() {
    const token = get(this.props, 'booking.token');
    if (token) return 'confirmation';
    if (this.state.bookingInProgress) return 'loading';
    return 'confirm';
  }

  getAvailableDateTimes(selectedDate) {
    const availableDates = get(this.props, 'userMediation.mediatedOccurences', []).map(o => o.beginningDatetime);
    const availableHours = availableDates.filter(d => moment(d).format('YYYY-MM-DD') === (selectedDate || this.state.date));
    return {
      availableDates,
      availableHours
    }
  }

  handleDateSelect = e => {
    const selectedDate = e.target.value;
    const {
      availableHours
    } = this.getAvailableDateTimes(selectedDate);
    this.setState({
      date: selectedDate,
      time: availableHours.length === 1 ? availableHours[0] : null
    })
  }

  render () {
    const token = get(this.props, 'booking.token');
    const price = get(this.props, 'offer.price');
    const step = this.currentStep();
    const dateRequired = get(this.props, 'userMediation.mediatedOccurences', []).length > 1;
    const dateOk = dateRequired ? (this.state.date && this.state.time) : true;
    const offerer = get(this.props, 'offer.offerer.name');
    const {
      availableDates,
      availableHours
    } = this.getAvailableDateTimes();
    return (
      <VersoWrapper>
        <div className='booking'>
          {step === 'confirm' && (
            <div>
              { dateRequired && (
                <div>
                  <h6>Choisissez une date :</h6>
                  <input type='date' className='input' list='available-dates' onChange={this.handleDateSelect} />
                  <datalist id='available-dates'>
                    { availableDates.map(d => <option key={d}>{moment(d).format('YYYY-MM-DD')}</option> ) }
                  </datalist>
                  <h6>Choisissez une heure :</h6>
                  <select value={this.state.time || ''} className='input' onChange={e => this.setState({time: e.target.value})} disabled={!this.state.date} >
                    { availableHours.length === 0 && <option></option>}
                    { availableHours.map(d =>
                      <option key={d} value={moment(d).format('H:mm')}>{moment(d).format('H:mm')}</option>
                    )}
                  </select>
                </div>
              )}
              { dateOk && (
                <div>
                  { Boolean(offerer) ? (
                    <div>
                      <p>Cette réservation d'une valeur de <Price value={price} /> vous est offerte par :<br />
                        <strong>{offerer}</strong>.
                      </p>
                      <p>Nous comptons sur vous pour en profiter !</p>
                    </div>
                  ) : (
                    <div>
                      <p>
                        Vous êtes sur le point de réserver cette offre pour <Price value={price} />.
                      </p>
                      <p>
                        <small>Le montant sera déduit de votre pass. Il vous restera <Price value={0} free='——' /> après cette réservation.</small>
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
          {step === 'loading' && (<p>Réservation en cours ...</p>)}
          {step === 'confirmation' && (
            <div className='booking__success center p3'>
              <Icon className='mb2' svg='picto-validation' />
              <p>Votre réservation est validée.</p>
              <p>
                { price > 0 && (<small><Price value={price} /> ont été déduits de votre pass.</small>) }
                <br />
                <small>Présentez le code suivant sur place :</small>
              </p>
              <p><big>{token}</big></p>
              <p><small>Retrouvez ce code et les détails de l'offre dans la rubrique "Mes réservations" de votre compte.</small></p>
            </div>
          )}
          <ul className='bottom-bar'>
            {step === 'confirm' && [
              <li key='submit'><button className={classnames({
                button: true,
                'button--primary': true,
                hidden: !dateOk,
              })} onClick={this.makeBooking}>Valider</button></li>,
              <li key='cancel'><button className='button button--secondary' onClick={e => this.props.closeModal()}>Annuler</button></li>,
            ]}
            {step === 'loading' && <li className='center'><Icon svg='loader-w' /></li>}
            {step === 'confirmation' && <li><button className='button button--secondary' onClick={e => this.props.closeModal()}>OK</button></li>}
          </ul>
        </div>
      </VersoWrapper>
    )
  }
}

export default connect(
  state => ({
    booking: selectBooking(state),
    offer: selectOffer(state),
    userMediation: selectUserMediation(state)
  }), {
  requestData,
  closeModal,
})(Booking)
