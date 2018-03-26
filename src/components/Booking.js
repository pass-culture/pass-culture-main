import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from '../components/Icon'
import { requestData } from '../reducers/data'

class Booking extends Component {
  constructor () {
    super ()
    this.state = {
      bookingInProgress: false,
      token: null,
      date: null,
      time: null,
    }
  }

  onClickConfirm() {
    this.setState({
      bookingInProgress: true
    })
    const { chosenOffer, id, requestData } = this.props
    requestData('POST', 'bookings', {
      body: {
        offerId: chosenOffer.id,
        quantity: 1,
        userMediationId: id
      }
    })
  }

  // handleSetToken(props) {
  //   if (!props.token && props.booking) {
  //     this.setState({ props.booking.token })
  //   }
  // }

  // componentWillMount () {
  //   this.handleSetToken(this.props)
  // }

  // componentWillReceiveProps (nextProps) {
  //   this.handleSetToken(nextProps)
  // }

  showForm() {
    return !this.state.bookingInProgress && !this.props.token;
  }

  render () {
    return (
      <div className='booking'>
        {this.showForm() && (
          <div>
            <h6>Choisissez une date :</h6>
            <input type='date' className='input' onChange={e => this.setState({date: e.target.value})} />
            <h6>Choisissez une heure :</h6>
            <input type='time' className='input' onChange={e => this.setState({time: e.target.value})} disabled={!this.state.date} />
            {this.state.date && this.state.time && (
              <div>
                <p>
                  Vous êtes sur le point de réserver cette offre pour ${this.props.price}.
                </p>
                <p>
                  <small>Le montant sera déduit de votre pass. Il vous restera O€ après cette réservation.</small>
                </p>
              </div>
            )}
          </div>
        )}
        {this.state.bookingInProgress && (<p>Réservation en cours ...</p>)}
        {this.token && (
          <div>
            <p>Votre réservation est validée.</p>
            <p>
              <small>8€ ont été déduits de votre pass.</small>
              <br />
              <small>Présentez le code suivant sur place :</small>
            </p>
            <p><big>{this.token}</big></p>
            <p><small>Retrouvez ce code et les détails de l'offre dans la rubrique "Mes réservations" de votre compte.</small></p>

          </div>
        )}
        <ul className='bottom-bar'>
          {this.showForm() && (
            <li><button className='button button--secondary' onClick={e => this.props.onClickCancel(e)}>Annuler</button></li>
          )}
          {this.showForm() && this.state.date && this.state.time && (
            <li><button className='button button--primary' onClick={e => this.onClickConfirm(e)}>Valider</button></li>
          )}
          {this.state.bookingInProgress && <li><Icon svg='loader-w' /></li>}
          {this.token && <li><button className='button button--secondary' onClick={e => this.props.onClickFinish(e)}>OK</button></li>}
        </ul>
      </div>
    )
  }
}

export default connect(
  state => ({
    booking: state.data.bookings && state.data.bookings[0],
    token: state.data.bookings[0].token
  }),
  {requestData},
)(Booking)
