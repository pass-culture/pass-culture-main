import React from 'react'
import { NavLink } from 'react-router-dom'
import { ROOT_PATH } from '../../utils/config'

const Logo = ({ className }) => {
  return (
    <NavLink to='/accueil' className={`logo ${className || ''}`} isActive={() => false}>
      <img src={`${ROOT_PATH}/icon/app-icon-app-store.png`} alt="Logo" />
      <strong>pass</strong>culture <sub>PRO</sub>
    </NavLink>
  )
}

export default Logo
