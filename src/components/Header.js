import React from 'react'
import { connect } from 'react-redux'

import Hamburger from './Hamburger'
import { THUMBS_URL } from '../utils/config'

const Header = ({ user, venue }) => {
  return (
    <div className='header flex items-center justify-start p2'>
      <Hamburger className='hamburger mr1'/>
      <div className='header__logo'>Pass Culture</div>
      <div className='flex-auto' />
      {
        user && venue && (
          <div className='header__venue flex items-center'>
            <span className='mx1'>
              {venue.name}
            </span>
            <img className='header__venue__image mr2'
              alt='venue'
              src={`${THUMBS_URL}/venues/${venue.id}`} />
          </div>
        )
      }
      {
        user && (
          <img className='header__avatar'
            alt='avatar'
            src={`${THUMBS_URL}/users/${user.id}`} />
        )
      }
      {
        user && !venue && (
          <div className='header__account-balance'>
            {user.account}{user.account ? '€' : ''}
          </div>
        )
      }
    </div>
  )
}

export default connect(
  ({ user }) => ({
    user,
    venue: user && user.userVenues && user.userVenues[0] && user.userVenues[0].venue
  })
)(Header)
