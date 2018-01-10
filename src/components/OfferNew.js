import React, { Component } from 'react'
import { connect } from 'react-redux'

import OfferForm from './OfferForm'
import { showModal } from '../reducers/modal'

class OfferNew extends Component {
  onNewClick = () => {
    this.props.showModal(<OfferForm />)
  }
  render () {
    return (
      <div className='flex items-center justify-center p1'>
        <button className='button button--alive button--inversed'
          onClick={this.onNewClick}
        >
          New
        </button>
      </div>
    )
  }
}

export default connect(null, { showModal })(OfferNew)
