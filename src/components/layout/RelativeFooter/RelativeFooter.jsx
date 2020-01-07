import PropTypes from 'prop-types'
import React from 'react'
import { Link, withRouter } from 'react-router-dom'

import ProfilePicture from '../ProfilePicture/ProfilePicture'

const RelativeFooter = ({ extraClassName, disabled, location, theme }) => {
  const cleanPath = location.pathname.replace(/\/$/, '')
  const menuUrl = `${cleanPath}/menu${location.search}`
  const colored = cleanPath === '/favoris' || cleanPath === '/reservations' ? '' : 'colored'

  return (
    <footer className={`pc-theme-${theme} pc-footer flex-center flex-none ${extraClassName}`}>
      <Link
        className={`no-border no-background no-outline no-select pc-theme-${theme}`}
        disabled={disabled}
        id="open-menu-button"
        to={menuUrl}
      >
        <ProfilePicture
          alt="Mon menu"
          colored={colored}
        />
      </Link>
    </footer>
  )
}

RelativeFooter.defaultProps = {
  disabled: false,
  extraClassName: '',
}

RelativeFooter.propTypes = {
  disabled: PropTypes.bool,
  extraClassName: PropTypes.string,
  location: PropTypes.shape().isRequired,
  theme: PropTypes.string.isRequired,
}

export default withRouter(RelativeFooter)
