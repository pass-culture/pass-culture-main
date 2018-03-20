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
      <div className='control-bar'>
        <button className='button'
          onClick={() => this.onPinClick('dislike')}>
          Jeter
        </button>
        <button className='button'
          onClick={() => this.onPinClick('interesting')} >
          Garder de côté
        </button>
        <button className='button'
          onClick={() => this.onBookClick} >
          J'y vais !
        </button>
      </div>
    )
  }
}

export default connect(
  state => ({ userId: state.user && state.user.id }),
  { requestData }
)(ControlBar)
