import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import { NavLink } from 'react-router-dom'

import { ROOT_PATH } from '../../utils/config'

const Logo = ({ className, noLink, whiteHeader, signPage }) => {
  let src
  if (whiteHeader) {
    src = `${ROOT_PATH}/icon/logo-full-hppro.png`
  } else src = `${ROOT_PATH}/icons/brand-logo-pro-small-pro.png`

  if (!whiteHeader && signPage) {
    src = `${ROOT_PATH}/icons/logo-group-splash@2x.png`
  }

  const extraProps = {}
  if (noLink) {
    extraProps.onClick = e => e.preventDefault()
  }
  return (
    <NavLink
      className={classnames('logo', className, { 'no-link': noLink })}
      to="/accueil"
      {...extraProps}
    >
      <img
        alt="Logo"
        src={src}
      />
      {signPage && (
        <div className="logo-subtitle">
          {'L’espace pass Culture des '}
          <span className="logo-subtitle-highlighted">
            {'acteurs culturels'}
          </span>
        </div>
      )}
    </NavLink>
  )
}

Logo.defaultProps = {
  className: '',
  noLink: false,
  signPage: false,
  whiteHeader: false,
}

Logo.propTypes = {
  className: PropTypes.string,
  noLink: PropTypes.bool,
  signPage: PropTypes.bool,
  whiteHeader: PropTypes.bool,
}

export default Logo
