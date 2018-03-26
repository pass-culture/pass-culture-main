import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../reducers/data'
import Icon from './Icon'

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
          <button className='button button--primary button--go'
            onClick={onClickBook} >
            <span className='price'>{`${chosenOffer.price}€`}</span>
            {
              (
                booking ||
                (userMediationBookings && userMediationBookings.length > 0)
              )
                ? 'Réservé'
                : 'J\'y vais!'
            }
          </button>
        </li>
      </ul>
    )
  }
}

export default connect(
  state => ({
    booking: state.data.bookings && state.data.bookings[0],
    userId: state.user && state.user.id
  }),
  { requestData }
)(ControlBar)
