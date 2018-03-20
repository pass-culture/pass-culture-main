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
    const { onClickBook, onClickFavorite, onClickShare } = this
    return (
      <div className='flex items-center flex-justify justify-around p2'>
        <button className='button button--alive mr1'
          onClick={onClickFavorite}>
          <img src='/icons/ico-like-w.svg' />
        </button>
        <button className='button button--alive mr1'
          onClick={onClickShare} >
          <img src='/icons/ico-share-w.svg' />
        </button>
        <button className='button button--alive'
          onClick={onClickBook} >
          Réserver
        </button>
      </div>
    )
  }
}

export default connect(
  state => ({ userId: state.user && state.user.id }),
  { requestData, showModal }
)(ControlBar)
