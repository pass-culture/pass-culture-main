import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from './Icon'
import OfferNew from './OfferNew'
import { showModal } from '../reducers/modal'

class OfferNewButton extends Component {
  onNewClick = () => {
    this.props.showModal(<OfferNew />)
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

export default connect(null, { showModal })(OfferNewButton)
