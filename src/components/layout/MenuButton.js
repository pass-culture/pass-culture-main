import React, { Component } from 'react'
import { connect } from 'react-redux'

import { showModal } from '../../reducers/modal'
import Menu from '../Menu'

class MenuButton extends Component {
  render () {
    const {
      showModal,
    } = this.props
    return (
      <button
        onClick={e => showModal(<Menu />)}
        style={{ backgroundImage: "url('../icons/pc_small.jpg')" }}
        className='discovery-page__profile' />
    )
  }
}

export default connect(
  state => ({}),
  { showModal }
)(MenuButton)
