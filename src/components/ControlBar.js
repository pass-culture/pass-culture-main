import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../reducers/data'

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
      <div className='flex items-center flex-justify justify-around p2'>
        <button className='button button--alive mr1'
          onClick={() => this.onPinClick('dislike')}>
          Jeter
        </button>
        <button className='button button--alive mr1'
          onClick={() => this.onPinClick('interesting')} >
          Garder de côté
        </button>
        <button className='button button--alive'
          onClick={() => this.onBookClick} >
          Réserver
        </button>
      </div>
    )
  }
}

export default connect(
  state => ({ userId: state.user && state.user.id }),
  { requestData }
)(ControlBar)
