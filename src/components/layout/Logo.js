import React from 'react'
import { NavLink } from 'react-router-dom'
import { ROOT_PATH } from '../../utils/config'

const Logo = ({ className, whiteHeader }) => {
  return (
    <NavLink to='/accueil' className={`logo ${className || ''}`} isActive={() => false}>
    {whiteHeader ? (<img src={`${ROOT_PATH}/icon/app-icon-spotlight.svg`} alt="Logo" />)
    : (
      <img src={`${ROOT_PATH}/icon/app-icon-app-store.png`} alt="Logo" />
    )
    }
    {/* {isLoggedIn ? (
     <LogoutButton onClick={this.handleLogoutClick} />
   ) : (
     <LoginButton onClick={this.handleLoginClick} />
   )} */}
      <strong>pass</strong>culture <sub>PRO</sub>
    </NavLink>
  )
}

export default Logo
