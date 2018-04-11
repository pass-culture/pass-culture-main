import React, { Component } from 'react'
import { connect } from 'react-redux'
import get from 'lodash.get';
import classnames from 'classnames';

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

  componentDidMount() {
    if (!get(this.props, 'offer.occurencesAtVenue')) {
      // Delay added because otherwise the AJAX call is too fast.
      // Remove when actual booking takes longer
      setTimeout(this.makeBooking, 500)
      this.setState({
        bookingInProgress: true
      })
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
    return 'input';
  }

  render () {
    const token = get(this.props, 'booking.token');
    const price = get(this.props, 'offer.price');
    const step = this.currentStep();
    return (
      <VersoWrapper>
        <div className='booking'>
          {step === 'input' && (
            <div>
              <h6>Choisissez une date :</h6>
              <input type='date' className='input' onChange={e => this.setState({date: e.target.value})} />
              <h6>Choisissez une heure :</h6>
              <input type='time' className='input' onChange={e => this.setState({time: e.target.value})} disabled={!this.state.date} />
              {this.state.date && this.state.time && (
                <div>
                  <p>
                    Vous êtes sur le point de réserver cette offre pour <Price value={price} />.
                  </p>
                  <p>
                    <small>Le montant sera déduit de votre pass. Il vous restera O€ après cette réservation.</small>
                  </p>
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
                <small><Price value={price} /> ont été déduits de votre pass.</small>
                <br />
                <small>Présentez le code suivant sur place :</small>
              </p>
              <p><big>{token}</big></p>
              <p><small>Retrouvez ce code et les détails de l'offre dans la rubrique "Mes réservations" de votre compte.</small></p>
            </div>
          )}
          <ul className='bottom-bar'>
            {step === 'input' && [
              <li key='submit'><button className={classnames({
                button: true,
                'button--primary': true,
                hidden: !(this.state.date && this.state.time)
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
