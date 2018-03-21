import React, { Component } from 'react'
import { connect } from 'react-redux'

import Booking from './Booking'
import { requestData } from '../reducers/data'
import { showModal } from '../reducers/modal'
import Icon from './Icon'

class ControlBar extends Component {
  onClickBook = () => {
    const { showModal } = this.props
    showModal(<Booking {...this.props} />)
  }
  onClickFavorite = type => {
    const { id, requestData } = this.props
    requestData('POST', 'userMediations', { body: [{ id,
      isFavorite: true
    }] })
  }
  render () {
    const { onClickBook,
      onClickFavorite,
      onClickShare
    } = this
    const { booking, userMediationBookings } = this.props
    return (
      <ul className='control-bar'>
        <li><small className='pass-label'>Mon pass</small><span className='pass-value'>476€</span></li>
        <li>
          <button className='button button--icon button--xlarge'
            onClick={onClickFavorite} >
            <Icon svg={this.props.isFavorite ? 'ico-like-w' : 'ico-like-w'} />
          </button>
        </li>
        <li>
          <button className='button button--icon button--xlarge'
            onClick={onClickShare}>
            <Icon svg='ico-share-w' />
          </button>
        </li>
        <li>
          <button className='button button-go'
            onClick={onClickBook} >
            <span className='price'>{`${this.props.userMediationOffers[0].price}€`}</span>
            {
              (
                booking ||
                (userMediationBookings && userMediationBookings.length > 0)
              )
                ? 'Mes réservations'
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
  { requestData, showModal }
)(ControlBar)
