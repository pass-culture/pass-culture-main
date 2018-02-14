import React from 'react'
import { connect } from 'react-redux'

import Hamburger from './Hamburger'
import Loading from './Loading'
import { THUMBS_URL } from '../utils/config'

const Header = ({ isPro, user }) => {
  return (
    <div className='header flex flex-wrap items-center justify-start p2'>
      <Hamburger className='hamburger mr1'/>
      <div className='header__logo mr1'>Pass Culture {isPro && (<i> PRO </i>)} </div>
      <Loading />
      <div className='flex-auto' />
      {
        user && (
          <img className='header__avatar'
            alt='avatar'
            src={`${THUMBS_URL}/users/${user.id}`} />
        )
      }
      {
        user && user.account && (
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
    isPro: user && user.userOfferers && user.userOfferers[0],
    user
  })
)(Header)
