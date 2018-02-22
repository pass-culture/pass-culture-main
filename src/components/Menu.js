import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import Link from './Link'
import { closeNavigation } from '../reducers/navigation'

class Menu extends Component {
  onLinkClick = href => {
    const { closeNavigation, history: { push } } = this.props
    push(href)
    closeNavigation()
  }
  render () {
    const { isNavigationActive, user } = this.props
    return (
      <div className={classnames('menu', { 'menu--active': isNavigationActive })}>
        <Link className={classnames('link block menu__link mb2', {
            'menu__link--active': '/decouverte' === window.location.pathname
          })}
          onClick={() => this.onLinkClick('/decouverte')}>
          Découverte
        </Link>
        {
          user && user.userOfferers && user.userOfferers.length > 0 && (
            <Link className={classnames('link block menu__link mb2', {
                'menu__link--active': '/pro' === window.location.pathname
              })}
              onClick={() => this.onLinkClick('/pro')}>
              Pro
            </Link>
          )
        }
        <Link className={classnames('link block menu__link mb2', {
            'menu__link--active': window.location.pathname === '/inventaire'
          })}
          onClick={() => this.onLinkClick('/inventaire')}
        >
          Inventaire
        </Link>
        <Link className={classnames('link block menu__link mb2', {
            'menu__link--active': window.location.pathname === '/profile'
          })}
          onClick={() => this.onLinkClick('/profile')}>
          Profile
        </Link>
      </div>
    )
  }
}

export default compose(
  // withRouter is necessary to  make update the component
  // given a location path change
  withRouter,
  connect(
    state => ({
      isNavigationActive: state.navigation.isActive,
      user: state.user
    }),
    { closeNavigation }
  )
)(Menu)
