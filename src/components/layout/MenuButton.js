import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'

import { showModal } from '../../reducers/modal'
import Menu from '../Menu'

class MenuButton extends Component {
  render () {
    const {
      isNavigationActive,
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
  state => ({
    isNavigationActive: state.navigation.isActive,
  }),
  { showModal }
)(MenuButton)
