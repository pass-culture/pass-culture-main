import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Transition } from 'react-transition-group'

import CloseLink from '../layout/Header/CloseLink'
import getMenuRoutes from './getMenuRoutes'
import Header from './Header'
import NavLink from './NavLink'
import SignoutButtonContainer from './SignoutButtonContainer'
import SimpleLink from './SimpleLink'

class Menu extends PureComponent {
  componentDidMount() {
    const { toggleOverlay } = this.props
    toggleOverlay()
  }

  componentWillUnmount() {
    const { toggleOverlay } = this.props
    toggleOverlay()
  }

  urlWithoutMenuElement = history => () => history.location.pathname.replace('/menu', '')

  render() {
    const { currentUser, history, readRecommendations, routes } = this.props
    const menuRoutes = getMenuRoutes(routes)

    return (
      <Transition
        appear
        in
        timeout={250}
      >
        {status => (
          <div
            className={`is-overlay ${status}`}
            id="main-menu"
          >
            <div className="inner is-full-layout is-relative flex-rows flex-end">
              <div
                className="pc-theme-red is-relative pc-scroll-container"
                id="main-menu-fixed-container"
              >
                <CloseLink
                  closeTitle="Fermer la navigation"
                  closeTo={this.urlWithoutMenuElement(history)()}
                />
                {currentUser && <Header currentUser={currentUser} />}
                <nav className="flex-rows pb0" id="main-menu-navigation">
                  {menuRoutes.map(route =>
                    route.href ? (
                      <SimpleLink
                        item={route}
                        key={route.href}
                      />
                    ) : (
                      <NavLink
                        item={route}
                        key={route.path}
                      />
                    )
                  )}
                  <SignoutButtonContainer
                    history={history}
                    readRecommendations={readRecommendations}
                  />
                </nav>
              </div>
            </div>
          </div>
        )}
      </Transition>
    )
  }
}

Menu.defaultProps = {
  currentUser: null,
}

Menu.propTypes = {
  currentUser: PropTypes.shape(),
  history: PropTypes.shape().isRequired,
  readRecommendations: PropTypes.arrayOf(PropTypes.shape().isRequired).isRequired,
  routes: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  toggleOverlay: PropTypes.func.isRequired,
}

export default Menu
