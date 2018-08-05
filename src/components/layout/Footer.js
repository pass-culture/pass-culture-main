import PropTypes from 'prop-types'
import classnames from 'classnames'
import { showModal } from 'pass-culture-shared'
import React from 'react'
import { connect } from 'react-redux'

import ProfilePicture from './ProfilePicture'
import Menu from '../Menu'

class Footer extends React.PureComponent {
  onClick = () => {
    const { dispatchShowModal } = this.props
    dispatchShowModal(<Menu />, { zIndex: 10002 })
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
          <button
            className="profile-button"
            onClick={this.onClick}
            type="button"
          >
            <ProfilePicture alt="Mon menu" {...maybeColored} />
          </button>
        </div>
      </footer>
    )
  }
}

Footer.defaultProps = {
  colored: false,
  onTop: false,
}

Footer.propTypes = {
  borderTop: PropTypes.bool.isRequired,
  colored: PropTypes.bool,
  dispatchShowModal: PropTypes.func.isRequired,
  isFlipped: PropTypes.bool.isRequired,
  onTop: PropTypes.bool,
}

export default connect(
  state => ({ isFlipped: state.verso.isFlipped }),
  {
    dispatchShowModal: showModal,
  }
)(Footer)
