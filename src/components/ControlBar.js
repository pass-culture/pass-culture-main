import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../reducers/data'
import Icon from './Icon'

class ControlBar extends Component {
  onBookClick = () => {
    // here we implement the api
    // to boo an offer...
  }
  onPinClick = type => {
    const { offerId, requestData, userId } = this.props
    requestData('POST', 'pins', {
      offerId,
      type,
      userId
    })
  }
  render () {
    return (
      <ul className='control-bar'>
        <li><small className='pass-label'>Mon pass</small><span className='pass-value'>476€</span></li>
        <li>
          <button className='button button--icon button--xlarge'
            onClick={() => this.onPinClick('interesting')} >
            <Icon name={this.props.isFavorite ? 'Favorite' : 'FavoriteOutline'} />
          </button>
        </li>
        <li>
          <button className='button button--icon button--xlarge'
            onClick={() => this.onPinClick('dislike')}>
            <Icon name='PresentToAll' />
          </button>
        </li>
        <li>
          <button className='button button-go'
            onClick={() => this.onBookClick} >
            <span className='price'>{`${this.props.userMediationOffers[0].price}€`}</span>
            J'y vais !
          </button>
        </li>
      </ul>
    )
  }
}

export default connect(
  state => ({ userId: state.user && state.user.id }),
  { requestData }
)(ControlBar)
