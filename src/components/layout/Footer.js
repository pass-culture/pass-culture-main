import classnames from 'classnames'
import { showModal } from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import ProfilePicture from './ProfilePicture'
import Menu from '../Menu'

class MenuButton extends Component {
  onClick = () => {
    this.props.showModal(<Menu />, { zIndex: 10002 })
  }

  render() {
    const { borderTop, colored, isFlipped, onTop } = this.props
    const maybeColored = {}
    if (colored) {
      maybeColored.colored = 'colored'
    }
    const style = {}
    if (!colored) {
      style.display = isFlipped ? 'none' : 'block'
    }
    return (
      <footer
        className={classnames('footer', {
          bordered: borderTop,
          colored,
          'on-top': onTop,
        })}
        style={style}
      >
        <div className="button-wrapper">
          <button className="profile-button" onClick={this.onClick} type="button">
            <ProfilePicture alt="Mon menu" {...maybeColored} />
          </button>
        </div>
      </footer>
    )
  }
}

export default connect(
  state => ({ isFlipped: state.verso.isFlipped }),
  {
    showModal,
  }
)(MenuButton)
