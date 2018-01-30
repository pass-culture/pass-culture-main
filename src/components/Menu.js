import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Link from './Link'

const Menu = ({ isNavigationActive, user }) => {
  return (
    <div className={classnames('menu', { 'menu--active': isNavigationActive })}>
      <Link className={classnames('link block menu__link mb2', {
          'menu__link--active': window.location.pathname === '/profile'
        })}
        href='/profile'>
        Profile
      </Link>
      <Link className={classnames('link block menu__link mb2', {
          'menu__link--active': ['/offres', '/gestion'].includes(window.location.pathname)
        })}
        href={user && user.seller ? '/gestion' : '/offres' }>
        {user && user.seller ? 'Offres' : 'Explore' }
      </Link>
      {
        user && !user.seller  && (
          <Link className={classnames('link block menu__link mb2', {
              'menu__link--active': window.location.pathname === '/inventaire'
            })}
            href='/inventaire'
          >
            Inventaire
          </Link>
        )
      }
    </div>
  )
}

export default compose(
  // withRouter is necessary to  make update the component
  // given a location path change
  withRouter,
  connect(
    state => ({
      isNavigationActive: state.navigation.isActive,
      user: state.user
    })
  )
)(Menu)
