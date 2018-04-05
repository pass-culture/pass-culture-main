import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Link } from "react-router-dom";

import { requestData } from '../reducers/data'
import { showModal } from '../reducers/modal'
import Icon from './Icon'
import Booking from './Booking'
import selectBooking from '../selectors/booking'
import selectOffer from '../selectors/offer'
import selectUserMediation from '../selectors/userMediation'


class ControlBar extends Component {

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

  render () {
    const { isFavorite, offer } = this.props
    return (
      <ul className='control-bar'>
        <li>
          <small className='pass-label'>Mon pass</small>
          <span className='pass-value'>0€</span>
        </li>
        <li>
          <button className='button button--secondary'
            onClick={e => this.onClickFavorite(e)} >
            <Icon svg={isFavorite ? 'ico-like-w' : 'ico-like-w'} />
          </button>
        </li>
        <li>
          <button className='button button--secondary'
            onClick={e => this.onClickShare(e)}>
            <Icon svg='ico-share-w' />
          </button>
        </li>
        <li>
          { this.props.booking ? (
            <Link to="/reservations" className='button button--primary button--inversed button--go'>
              <Icon name='Check' />
              {' Réservé'}
            </Link>
          ) : (
            <button className='button button--primary button--go'
              onClick={e => this.props.showModal(<Booking />, {fullscreen: true, maskColor: 'transparent', hasCloseButton: false})} >
              <span className='price'>{`${offer && offer.price}€`}</span>
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
