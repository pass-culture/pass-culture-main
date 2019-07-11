import classnames from 'classnames'
import React from 'react'
import { NavLink } from 'react-router-dom'

import { ROOT_PATH } from '../../utils/config'

const Logo = ({ className, noLink, whiteHeader, signPage }) => {
  let src
  if (whiteHeader) {
    src = `${ROOT_PATH}/icon/logo-full-hppro.png`
  } else src = `${ROOT_PATH}/icons/logo-inline-negative.png`

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
      isActive={() => false}
      to="/accueil"
      {...extraProps}
    >
      <img
        alt="Logo"
        src={src}
      />
    </NavLink>
  )
}

export default Logo
