import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import { NavLink } from 'react-router-dom'

import { ROOT_PATH } from 'utils/config'

const Logo = ({ className, noLink, onClick, signPage, isUserAdmin }) => {
  let src = `${ROOT_PATH}/icons/brand-logo-pro-small-pro.png`
  if (signPage) {
    src = `${ROOT_PATH}/icons/logo-pass-culture-white.svg`
  }

  const handleClick = noLink ? e => e.preventDefault() : onClick

  return (
    <NavLink
      className={classnames('logo', className, { 'no-link': noLink })}
      onClick={handleClick}
      to={isUserAdmin ? '/structures' : '/accueil'}
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
  onClick: () => {},
  signPage: false,
}

Logo.propTypes = {
  className: PropTypes.string,
  isUserAdmin: PropTypes.bool,
  noLink: PropTypes.bool,
  onClick: PropTypes.func,
  signPage: PropTypes.bool,
}

export default Logo
