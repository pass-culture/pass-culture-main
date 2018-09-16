/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { Transition } from 'react-transition-group'
import { Scrollbars } from 'react-custom-scrollbars'
import { withRouter } from 'react-router-dom'

import routes from '../utils/routes'
import MenuItem from './menu/MenuItem'
import MenuHeader from './menu/MenuHeader'
import MenuSignoutButton from './menu/MenuSignoutButton'
import { toggleMainMenu } from '../reducers/menu'
import { getMainMenuItems } from '../utils/routes-utils'

const transitionDelay = 250
const transitionDuration = 250
const menuitems = getMainMenuItems(routes)

const defaultStyle = {
  opacity: '0',
  top: '100%',
  transitionDuration: `${transitionDuration}ms`,
  transitionProperty: 'opacity, top',
  transitionTimingFunction: 'ease',
}

const transitionStyles = {
  entered: { opacity: 1, top: 0 },
  entering: { opacity: 0, top: '100%' },
}

class MainMenu extends React.PureComponent {
  toggleMainMenu = () => {
    const { dispatch } = this.props
    dispatch(toggleMainMenu())
  }

  renderCloseButton = () => (
    <button
      type="button"
      id="main-menu-close-button"
      className="pc-text-button is-white-text is-absolute fs16"
      onClick={this.toggleMainMenu}
    >
      <span aria-hidden className="icon-close" title="Fermer la navigation" />
    </button>
  )

  renderNavigationLinks = () => (
    <React.Fragment>
      {menuitems &&
        menuitems.map(
          obj =>
            obj && (
              <MenuItem
                item={obj}
                key={obj.path || obj.href}
                clickHandler={this.toggleMainMenu}
              />
            )
        )}
      <MenuSignoutButton />
    </React.Fragment>
  )

  render() {
    const { isVisible, user } = this.props
    return (
      <Transition in={isVisible} timeout={transitionDelay}>
        {state => (
          <div
            id="main-menu"
            className="is-overlay p12 flex-rows flex-end"
            style={{ ...defaultStyle, ...transitionStyles[state] }}
          >
            <div className="inner is-relative is-clipped">
              {this.renderCloseButton()}
              <div id="main-menu-fixed-container">
                <Scrollbars autoHide>
                  <div className="scroll-container pc-theme-red">
                    <MenuHeader user={user} />
                    {/* <!-- Navigation Items --> */}
                    <nav
                      id="main-menu-navigation"
                      className="flex-rows mt16 pb0"
                    >
                      {this.renderNavigationLinks()}
                    </nav>
                    {/* <!-- Navigation Items --> */}
                  </div>
                </Scrollbars>
              </div>
            </div>
          </div>
        )}
      </Transition>
    )
  }
}

MainMenu.defaultProps = {
  user: null,
}

MainMenu.propTypes = {
  dispatch: PropTypes.func.isRequired,
  isVisible: PropTypes.bool.isRequired,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]),
}

const mapStateToProps = state => ({
  isVisible: state.menu,
  user: state.user,
})

export default compose(
  withRouter,
  connect(mapStateToProps)
)(MainMenu)
