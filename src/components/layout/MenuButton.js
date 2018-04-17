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
      colored,
      isFlipped
    } = this.props
    const maybeColored = {}
    if (colored) {
      maybeColored.colored = "colored"
    }
    const style = {}
    if (!colored) {
      style.display = isFlipped
        ? 'none'
        : 'block'
    }
    return (
      <div className={classnames('menu-button', {
        bordered: borderTop,
        colored: colored,
      })} style={style}>
        <button onClick={this.onClick}>
          <ProfilePicture {... maybeColored} />
        </button>
      </div>
    )
  }
}

export default connect(
  state => ({ isFlipped: state.verso.isFlipped }),
  { showModal }
)(MenuButton)
