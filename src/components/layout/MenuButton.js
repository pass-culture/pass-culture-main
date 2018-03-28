import React, { Component } from 'react'
import { connect } from 'react-redux'
import classnames from 'classnames'

import { showModal } from '../../reducers/modal'
import Menu from '../Menu'
import ProfilePicture from '../ProfilePicture'

class MenuButton extends Component {
  render () {
    const {
      showModal,
    } = this.props
    return (
      <div className={classnames('menu-button', {
        bordered: this.props.borderTop
      })}>
        <button onClick={e => showModal(<Menu />)} className={classnames({colored: this.props.colored})}>
          <ProfilePicture />
        </button>
      </div>
    )
  }
}

export default connect(
  state => ({}),
  { showModal }
)(MenuButton)
