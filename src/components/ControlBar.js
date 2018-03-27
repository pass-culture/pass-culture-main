import React, { Component } from 'react'
import { connect } from 'react-redux'
import { Link } from "react-router-dom";

import { requestData } from '../reducers/data'
import Icon from './Icon'
import currentBooking from '../selectors/currentBooking'
import currentUserMediation from '../selectors/currentUserMediation'
import currentOffer from '../selectors/currentOffer'

class ControlBar extends Component {

  onClickFavorite(type) {
    this.props.requestData('POST', 'userMediations', {
      body: [{
        id: this.props.currentUserMediation.id,
        isFavorite: true
      }]
    })
  }

  onClickShare() {
    // TODO
  }

  render () {
    return (
      <ul className='control-bar'>
        <li><small className='pass-label'>Mon pass</small><span className='pass-value'>0€</span></li>
        <li>
          <button className='button button--secondary'
            onClick={e => this.onClickFavorite(e)} >
            <Icon svg={this.props.isFavorite ? 'ico-like-w' : 'ico-like-w'} />
          </button>
        </li>
        <li>
          <button className='button button--secondary'
            onClick={e => this.onClickShare(e)}>
            <Icon svg='ico-share-w' />
          </button>
        </li>
        <li>
          { this.props.currentBooking ? (
            <Link to="/reservations" className='button button--primary button--inversed button--go'>
              <Icon name='Check' />
              {' Réservé'}
            </Link>
          ) : (
            <button className='button button--primary button--go'
              onClick={e => this.props.onClickBook()} >
              <span className='price'>{`${this.props.currentOffer.price}€`}</span>
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
    currentBooking: currentBooking(state),
    currentUserMediation: currentUserMediation(state),
    currentOffer: currentOffer(state),
  }), {
  requestData
})(ControlBar)
