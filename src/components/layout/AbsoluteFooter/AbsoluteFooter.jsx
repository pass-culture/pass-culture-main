import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import ProfilePicture from '../ProfilePicture/ProfilePicture'

const AbsoluteFooter = ({ areDetailsVisible, borderTop, colored, id, location, onTop }) => {
  const maybeColored = {}
  if (colored) {
    maybeColored.colored = 'colored'
  }
  const style = {}
  if (!colored) {
    style.display = areDetailsVisible ? 'none' : 'block'
  }
  const className = classnames('absolute-footer', {
    bordered: borderTop,
    colored,
    'on-top': onTop,
  })

  const cleanPath = location.pathname.replace(/\/$/, '')
  const menuUrl = `${cleanPath}/menu${location.search}`
  const footerProps = { className, style }
  if (id) {
    footerProps.id = id
  }
  return (
    <footer {...footerProps}>
      <div className="button-wrapper flex-center">
        <Link
          className="profile-button is-block text-center"
          style={{ paddingTop: '0.4rem' }}
          to={menuUrl}
        >
          <ProfilePicture
            alt="Mon menu"
            {...maybeColored}
          />
        </Link>
      </div>
    </footer>
  )
}

AbsoluteFooter.defaultProps = {
  colored: false,
  id: null,
  onTop: false,
}

AbsoluteFooter.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  borderTop: PropTypes.bool.isRequired,
  colored: PropTypes.bool,
  id: PropTypes.string,
  location: PropTypes.shape().isRequired,
  onTop: PropTypes.bool,
}

export default AbsoluteFooter
