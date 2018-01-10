import React from 'react'
import { connect } from 'react-redux'

import Hamburger from './Hamburger'
import SignButton from './SignButton'

const Header = ({ user }) => {
  return (
    <div className='header flex items-center justify-start p2'>
      <Hamburger className='hamburger mr1'/>
      <img className='header__logo' alt='logo' src='/logo.png' />
      <div className='flex-auto' />
      {
        user
          ? <img className='header__avatar' alt='avatar' src={user.thumbnailUrl} />
          : <SignButton />
      }
    </div>
  )
}

export default connect(
  ({ user }) => ({ user })
)(Header)
