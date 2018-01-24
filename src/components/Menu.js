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
          'menu__link--active': window.location.pathname === '/offres'
        })}
        href={user && user.type === 'client' ? '/offres' : '/gestion'}
      >
        Home
      </Link>
      {
        user && user.type === 'client' && [
          <Link className={classnames('link block menu__link mb2', {
              'menu__link--active': window.location.pathname === '/favoris'
            })}
            key={0}
            href='/favoris'
          >
            Mes favoris
          </Link>,

          <Link className={classnames('link block menu__link mb2', {
              'menu__link--active': window.location.pathname === '/panier'
            })}
            key={1}
            href='/panier'
          >
            Mon panier
          </Link>
        ]
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
