import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import { NavLink } from 'react-router-dom'

import { ROOT_PATH } from 'utils/config'

const Logo = ({ className, noLink, signPage, isUserAdmin }) => {
  let src = `${ROOT_PATH}/icons/brand-logo-pro-small-pro.png`
  if (signPage) {
    src = `${ROOT_PATH}/icons/logo-pass-culture-white.svg`
  }

  const extraProps = {}
  if (noLink) {
    extraProps.onClick = e => e.preventDefault()
  }
  return (
    <NavLink
      className={classnames('logo', className, { 'no-link': noLink })}
      to={isUserAdmin ? '/structures' : '/accueil'}
      {...extraProps}
    >
      <img
        alt="Pass Culture pro, l'espace Pass Culture des acteurs culturels"
        src={src}
      />
    </NavLink>
  )
}

Logo.defaultProps = {
  className: '',
  isUserAdmin: false,
  noLink: false,
  signPage: false,
}

Logo.propTypes = {
  className: PropTypes.string,
  isUserAdmin: PropTypes.bool,
  noLink: PropTypes.bool,
  signPage: PropTypes.bool,
}

export default Logo
