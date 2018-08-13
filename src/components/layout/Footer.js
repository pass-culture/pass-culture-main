import PropTypes from 'prop-types'
import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'

import ProfilePicture from './ProfilePicture'
import { toggleMainMenu } from '../../reducers/menu'

const Footer = ({ borderTop, colored, isFlipped, onTop, dispatch }) => {
  const maybeColored = {}
  if (colored) {
    maybeColored.colored = 'colored'
  }
  const style = {}
  if (!colored) {
    style.display = isFlipped ? 'none' : 'block'
  }
  const cssclass = classnames('footer', {
    bordered: borderTop,
    colored,
    'on-top': onTop,
  })
  return (
    <footer className={cssclass} style={style}>
      <div className="button-wrapper">
        <button
          className="profile-button"
          onClick={() => dispatch(toggleMainMenu())}
          type="button"
        >
          <ProfilePicture alt="Mon menu" {...maybeColored} />
        </button>
      </div>
    </footer>
  )
}

Footer.defaultProps = {
  colored: false,
  onTop: false,
}

Footer.propTypes = {
  borderTop: PropTypes.bool.isRequired,
  colored: PropTypes.bool,
  dispatch: PropTypes.func.isRequired,
  isFlipped: PropTypes.bool.isRequired,
  onTop: PropTypes.bool,
}

const mapStateToProps = state => ({ isFlipped: state.verso.isFlipped })

export default connect(mapStateToProps)(Footer)
