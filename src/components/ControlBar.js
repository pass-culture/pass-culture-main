import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Link } from "react-router-dom";
import get from 'lodash.get'

import { requestData } from '../reducers/data'
import { showModal } from '../reducers/modal'
import Icon from './Icon'
import Price from './Price'
import Booking from './Booking'
import selectBooking from '../selectors/booking'
import selectOffer from '../selectors/offer'
import selectUserMediation from '../selectors/userMediation'


class ControlBar extends Component {

  onClickDisable = event => {
    alert('Pas encore disponible')
    event.preventDefault()
  }

  onClickFavorite(type) {
    this.props.requestData('POST', 'userMediations', {
      body: [{
        id: this.props.userMediation.id,
        isFavorite: true
      }]
    })
  }

  onClickShare() {
    // TODO
  }

  onClickJyVais = event => {
    if (this.props.offer) {
        this.props.showModal(<Booking />, {fullscreen: true, maskColor: 'transparent', hasCloseButton: false})
    } else {
      alert("Ce bouton vous permet d'effectuer une reservation")
    }
  }

  render () {
    const {
      isFavorite,
      offer,
      booking
    } = this.props
    if (booking) {
      console.log('received booking', booking)
    }
    return (
      <ul className='control-bar'>
        <li><small className='pass-label'>Mon Pass</small><span className='pass-value'>——€</span></li>
        <li>
          <button className='button button--secondary disabled'
            onClick={this.onClickDisable} >
            <Icon svg={isFavorite ? 'ico-like-w' : 'ico-like-w'} />
          </button>
        </li>
        <li>
          <button className='button button--secondary disabled'
            onClick={this.onClickDisable}>
            <Icon svg='ico-share-w' />
          </button>
        </li>
        <li>
          { booking ? (
            <Link to="/reservations" className='button button--primary button--inversed button--go'>
              <Icon name='Check' />
              {' Réservé'}
            </Link>
          ) : (
            <button className='button button--primary button--go'
              onClick={this.onClickJyVais} >
              <Price value={get(offer, 'price')} free='——' />
              J'y vais!
            </button>
          )}
        </li>
      </ul>
    )
  }
}

export default connect(
  state => ({
    booking: selectBooking(state),
    userMediation: selectUserMediation(state),
    offer: selectOffer(state),
  }), {
  requestData,
  showModal,
})(ControlBar)
