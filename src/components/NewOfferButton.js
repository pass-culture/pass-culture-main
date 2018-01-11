import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from './Icon'
import NewOffer from './NewOffer'
import { showModal } from '../reducers/modal'

class NewOfferButton extends Component {
  onNewClick = () => {
    this.props.showModal(<NewOffer />)
  }
  render () {
    return (
      <div className='flex items-center justify-center p1'>
        <button className='button button--alive button--inversed'
          onClick={this.onNewClick}
        >
          <Icon name='add' />
        </button>
      </div>
    )
  }
}

export default connect(null, { showModal })(NewOfferButton)
