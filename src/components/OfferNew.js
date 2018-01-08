import React, { Component } from 'react'
import { connect } from 'react-redux'

import Button from './Button'
import OfferForm from './OfferForm'
import { showModal } from '../reducers/modal'

class OfferNew extends Component {
  constructor () {
    super()
    this.onNewClick = this._onNewClick.bind(this)
  }
  _onNewClick () {
    this.props.showModal(<OfferForm />)
  }
  render () {
    return (
      <div className='flex items-center justify-center p1'>
        <Button className='button button--alive button--inversed'
          onClick={this.onNewClick}
        >
          New
        </Button>
      </div>
    )
  }
}

export default connect(null, { showModal })(OfferNew)
