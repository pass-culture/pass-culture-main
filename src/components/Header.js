import React from 'react'
import { connect } from 'react-redux'

import Hamburger from './Hamburger'
import SignButton from './SignButton'
import { THUMBS_URL } from '../utils/config'

const Header = ({ user }) => {
  return (
    <div className='header flex flex-wrap items-center justify-start p2'>
      <Hamburger className='hamburger mr1'/>
      <div className='header__logo mr1'>
        Pass Culture {user && user.isPro && (<i> PRO </i>)}
      </div>
      <div id='header__content' />
      <div className='flex-auto' />
      {
        user ? (
          <img className='header__avatar'
            alt='avatar'
            src={`${THUMBS_URL}/users/${user.id}`} />
        ) : <SignButton />
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

export default connect(state => ({ user: state.user }))(Header)
