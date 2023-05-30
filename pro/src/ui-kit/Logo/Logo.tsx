import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import { NavLink } from 'react-router-dom'

import { ROOT_PATH } from 'utils/config'

const Logo = ({ className, noLink, onClick, signPage }: any) => {
  let src = `${ROOT_PATH}/icons/logo-pass-culture-header.svg`
  if (signPage) {
    src = `${ROOT_PATH}/icons/logo-pass-culture-white.svg`
  }

  return (
    <NavLink
      className={classnames('logo', className, { 'no-link': noLink })}
      onClick={noLink ? e => e.preventDefault() : onClick}
      to={'/accueil'}
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
  noLink: false,
  onClick: () => {},
  signPage: false,
}

Logo.propTypes = {
  className: PropTypes.string,
  noLink: PropTypes.bool,
  onClick: PropTypes.func,
  signPage: PropTypes.bool,
}

export default Logo
