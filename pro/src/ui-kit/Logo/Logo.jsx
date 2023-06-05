import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import { NavLink } from 'react-router-dom'

import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon.tsx'
import { ROOT_PATH } from 'utils/config'

const Logo = ({ className, noLink, onClick, signPage }) => {
  let src = `${ROOT_PATH}/icons/logo-pass-culture-header.svg`
  if (signPage) {
    src = `${ROOT_PATH}/icons/logo-pass-culture-primary.svg`
  }

  const handleClick = noLink ? e => e.preventDefault() : onClick

  return (
    <NavLink
      className={classnames('logo', className, { 'no-link': noLink })}
      onClick={handleClick}
      to={'/accueil'}
    >
      <SvgIcon
        className={classnames({ 'sign-height': signPage })}
        viewBox={classnames({ '0 0 282 120': signPage })}
        alt="Pass Culture pro, l'espace des acteurs culturels"
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
