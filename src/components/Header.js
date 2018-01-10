import React from 'react'
import { connect } from 'react-redux'

import Hamburger from './Hamburger'

const Header = ({ user }) => {
  return (
    <div className='header flex items-center justify-start p2'>
      <Hamburger className='hamburger mr1'/>
      <div className='header__logo'>Pass Culture</div>
      <div className='flex-auto' />
      {
        user
          ? <img className='header__avatar' alt='avatar' src={user.thumbnailUrl} />
          : undefined
      }
    </div>
  )
}

export default connect(
  ({ user }) => ({ user })
)(Header)
