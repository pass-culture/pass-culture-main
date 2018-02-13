import React from 'react'
import { connect } from 'react-redux'

import Hamburger from './Hamburger'
import Loading from './Loading'
import { THUMBS_URL } from '../utils/config'

const Header = ({ user, offerer }) => {
  return (
    <div className='header flex flex-wrap items-center justify-start p2'>
      <Hamburger className='hamburger mr1'/>
      <div className='header__logo mr1'>Pass Culture</div>
      <Loading />
      <div className='flex-auto' />
      {
        user && offerer && (
          <div className='header__offerer flex items-center justify-center mr1'>
            {
              /*
              <span className='mx1'>
                {offerer.name}
              </span>
              */
            }
            <img className='header__offerer__image'
              alt='offerer'
              src={`${THUMBS_URL}/offerers/${offerer.id}`} />
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
        user && !offerer && (
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
    offerer: user && user.userOfferers && user.userOfferers[0]
  })
)(Header)
