import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Transition } from 'react-transition-group'

import Header from './Header'
import NavLink from './NavLink'
import routes from '../../utils/routes'
import { getMenuRoutes } from '../../utils/routes-utils'
import SignoutButtonContainer from './SignoutButtonContainer'
import SimpleLink from './SimpleLink'

const menuRoutes = getMenuRoutes(routes)

class Menu extends PureComponent {
  componentDidMount() {
    const { toggleOverlay } = this.props
    toggleOverlay()
  }

  componentWillUnmount() {
    const { toggleOverlay } = this.props
    toggleOverlay()
  }

  render() {
    const { currentUser, history, readRecommendations } = this.props

    return (
      <Transition appear in timeout={250}>
        {status => (
          <div className={`is-overlay ${status}`} id="main-menu">
            <div className="inner is-full-layout is-relative flex-rows flex-end">
              <div
                className="pc-theme-red is-relative pc-scroll-container"
                id="main-menu-fixed-container"
              >
                <button
                  className="pc-text-button is-white-text is-absolute fs16"
                  id="main-menu-close-button"
                  onClick={history.goBack}
                  type="button"
                >
                  <span
                    aria-hidden
                    className="icon-legacy-close"
                    title="Fermer la navigation"
                  />
                </button>
                <Header currentUser={currentUser} />
                <nav className="flex-rows pb0" id="main-menu-navigation">
                  {menuRoutes.map(route =>
                    route.href ? (
                      <SimpleLink item={route} key={route.href} />
                    ) : (
                      <NavLink item={route} key={route.path} />
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

Menu.propTypes = {
  currentUser: PropTypes.shape().isRequired,
  history: PropTypes.shape().isRequired,
  readRecommendations: PropTypes.arrayOf(PropTypes.shape().isRequired)
    .isRequired,
  toggleOverlay: PropTypes.func.isRequired,
}

export default Menu
