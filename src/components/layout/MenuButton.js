import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import Menu from '../Menu'
import ProfilePicture from '../ProfilePicture'
import { showModal } from '../../reducers/modal'

class MenuButton extends Component {
  onClick = () => {
    this.props.showModal(<Menu />)
  }
  render () {
    const { borderTop,
      colored
    } = this.props
    return (
      <div className={classnames('menu-button', {
        bordered: borderTop
      })}>
        <button onClick={this.onClick}
          className={classnames({ colored })}>
          <ProfilePicture />
        </button>
      </div>
    )
  }
}

export default connect(
  null,
  { showModal }
)(MenuButton)
