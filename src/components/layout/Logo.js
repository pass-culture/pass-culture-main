import React from 'react'
import { NavLink } from 'react-router-dom'
import { ROOT_PATH } from '../../utils/config'

const Logo = ({ className, whiteHeader }) => {
  console.log(' ----- Logo whiteHeader ----- ', whiteHeader);
  return (
    <NavLink to='/accueil' className={`logo ${className || ''}`} isActive={() => false}>
    {whiteHeader ? (<img src={`${ROOT_PATH}/icon/app-icon-spotlight.svg`} alt="Logo" />)
    : (
      <img src={`${ROOT_PATH}/icons/logo-group-splash.svg`} alt="Logo" />
    )
    }
    </NavLink>
  )
}

export default Logo
