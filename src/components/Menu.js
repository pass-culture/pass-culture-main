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
          'menu__link--active': '/explore' === window.location.pathname
        })}
        href={'/explore'}>
        Explore
      </Link>
      {
        user && user.userOfferers && user.userOfferers.length > 0 && (
          <Link className={classnames('link block menu__link mb2', {
            'menu__link--active': '/gestion' === window.location.pathname
          })}
          href={'/gestion'}>
            Gestion
          </Link>
        )
      }
      <Link className={classnames('link block menu__link mb2', {
          'menu__link--active': window.location.pathname === '/inventaire'
        })}
        href='/inventaire'
      >
        Inventaire
      </Link>
      <Link className={classnames('link block menu__link mb2', {
          'menu__link--active': window.location.pathname === '/profile'
        })}
        href='/profile'>
        Profile
      </Link>
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
