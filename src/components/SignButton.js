import React, { Component } from 'react'
import { connect } from 'react-redux'

import Sign from './Sign'
import { closeModal, showModal } from '../reducers/modal'

class SignButton extends Component {
  componentWillUnmount (nextProps) {
    this.props.closeModal()
  }
  component
  onClick = () => {
    this.props.showModal(<Sign />)
  }
  render () {
    return (
      <button className='button button--alive' onClick={this.onClick} >
        Login
      </button>
    )
  }
}

export default connect(
  null,
  { closeModal, showModal }
)(SignButton)
