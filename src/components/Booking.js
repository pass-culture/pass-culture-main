import React, { Component } from 'react'
import { connect } from 'react-redux'
import get from 'lodash.get';

import Icon from '../components/Icon'
import { requestData } from '../reducers/data'
import currentBooking from '../selectors/currentBooking'
import currentUserMediation from '../selectors/currentUserMediation'
import currentOffer from '../selectors/currentOffer'

class Booking extends Component {
  constructor () {
    super ()
    this.state = {
      bookingInProgress: false,
      date: null,
      time: null,
    }
  }

  onClickConfirm() {
    this.setState({
      bookingInProgress: true
    })
    this.props.requestData('POST', 'bookings', {
      body: {
        offerId: currentOffer.id,
        quantity: 1,
        userMediationId: currentUserMediation.id
      }
    })
  }

  render () {
    const token = get(this.props, 'currentBooking.token');
    const inputStep = !this.state.bookingInProgress && !token;
    const loadingStep = this.state.bookingInProgress && !token;
    const confirmationStep = token;
    return (
      <div className='booking'>
        {inputStep && (
          <div>
            <h6>Choisissez une date :</h6>
            <input type='date' className='input' onChange={e => this.setState({date: e.target.value})} />
            <h6>Choisissez une heure :</h6>
            <input type='time' className='input' onChange={e => this.setState({time: e.target.value})} disabled={!this.state.date} />
            {this.state.date && this.state.time && (
              <div>
                <p>
                  Vous êtes sur le point de réserver cette offre pour {this.props.currentOffer.price}€.
                </p>
                <p>
                  <small>Le montant sera déduit de votre pass. Il vous restera O€ après cette réservation.</small>
                </p>
              </div>
            )}
          </div>
        )}
        {loadingStep && (<p>Réservation en cours ...</p>)}
        {confirmationStep && (
          <div>
            <p>Votre réservation est validée.</p>
            <p>
              <small>8€ ont été déduits de votre pass.</small>
              <br />
              <small>Présentez le code suivant sur place :</small>
            </p>
            <p><big>{token}</big></p>
            <p><small>Retrouvez ce code et les détails de l'offre dans la rubrique "Mes réservations" de votre compte.</small></p>

          </div>
        )}
        <ul className='bottom-bar'>
          {inputStep && (
            <li><button className='button button--secondary' onClick={e => this.props.onClickCancel(e)}>Annuler</button></li>
          )}
          {inputStep && this.state.date && this.state.time && (
            <li><button className='button button--primary' onClick={e => this.onClickConfirm(e)}>Valider</button></li>
          )}
          {loadingStep && <li><Icon svg='loader-w' /></li>}
          {token && <li><button className='button button--secondary' onClick={e => this.props.onClickFinish(e)}>OK</button></li>}
        </ul>
      </div>
    )
  }
}

export default connect(
  state => ({
    currentBooking: currentBooking(state),
    currentUserMediation: currentUserMediation(state),
    currentOffer: currentOffer(state),
  }), {
  requestData
})(Booking)
