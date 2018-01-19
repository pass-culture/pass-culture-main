import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from './Icon'
import OfferNew from './OfferNew'
import { resetForm } from '../reducers/form'
import { showModal } from '../reducers/modal'

class OfferNewButton extends Component {
  onNewClick = () => {
    const { resetForm, showModal } = this.props
    resetForm()
    showModal(<OfferNew />)
  }
  render () {
    return (
      <div className='flex items-center justify-center p1'>
        <button className='button button--alive button--rounded left-align'
          onClick={this.onNewClick}
        >
          <Icon name='add' />
        </button>
      </div>
    )
  }
}

export default connect(null, { resetForm, showModal })(OfferNewButton)
