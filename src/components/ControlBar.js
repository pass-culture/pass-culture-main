import React, { Component } from 'react'
import { connect } from 'react-redux'
import get from 'lodash.get';

import { requestData } from '../reducers/data'
import Icon from './Icon'
import currentBooking from '../selectors/currentBooking'
import currentUserMediation from '../selectors/currentUserMediation'

class ControlBar extends Component {

  onClickFavorite(type) {
    const { id, requestData } = this.props
    requestData('POST', 'userMediations', { body: [{ id,
      isFavorite: true
    }] })
  }

  render () {
    const {
      onClickFavorite,
      onClickShare
    } = this
    const {
      onClickBook,
      onClickViewBookings,
      booking,
      userMediationBookings,
      chosenOffer,
     } = this.props
    return (
      <ul className='control-bar'>
        <li><small className='pass-label'>Mon pass</small><span className='pass-value'>0€</span></li>
        <li>
          <button className='button button--secondary'
            onClick={onClickFavorite} >
            <Icon svg={this.props.isFavorite ? 'ico-like-w' : 'ico-like-w'} />
          </button>
        </li>
        <li>
          <button className='button button--secondary'
            onClick={onClickShare}>
            <Icon svg='ico-share-w' />
          </button>
        </li>
        <li>
          { !this.props.currentBooking &&
            <button className='button button--primary button--go'
              onClick={onClickBook} >
              <span className='price'>{`${chosenOffer.price}€`}</span>
              J'y vais!
            </button>
          }
          { this.props.currentBooking &&
            <button className='button button--primary button--inversed button--go'
              onClick={onClickViewBookings} >
              <Icon name='Check' />
              {' Réservé'}
            </button>
          }

        </li>
      </ul>
    )
  }
}

export default connect(
  state => ({
    currentBooking: currentBooking(state),
    currentUserMediation: currentUserMediation(state),
  }),
  { requestData }
)(ControlBar)
