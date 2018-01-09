import React from 'react'

import Hamburger from './Hamburger'

const Header = () => {
  return (
    <div className='header flex items-center justify-start p2'>
      <Hamburger className='hamburger mr1'/>
      <img className='header__logo' alt='logo' src='/logo.png' />
      <div className='flex-auto' />
      <img className='header__avatar' alt='avatar' src='/dragon.png' />
    </div>
  )
}

export default Header
