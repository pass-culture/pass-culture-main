/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import { Icon, requestData } from 'pass-culture-shared'
import React from 'react'
import { connect } from 'react-redux'
import { compose, bindActionCreators } from 'redux'
import { Transition } from 'react-transition-group'
import { Scrollbars } from 'react-custom-scrollbars'
import { withRouter } from 'react-router-dom'

import routes from '../utils/routes'
import MenuLink from './menu/MenuLink'
import MenuHeader from './menu/MenuHeader'
import { toggleMainMenu } from '../reducers/menu'
import { getMainMenuItems } from '../utils/routes-utils'

const transitionDelay = 250
const transitionDuration = 250
const menuitems = getMainMenuItems(routes)

const defaultStyle = {
  opacity: '0',
  top: '100vh',
  transitionDuration: `${transitionDuration}ms`,
  transitionProperty: 'opacity, top',
  transitionTimingFunction: 'ease',
}

const transitionStyles = {
  entered: { opacity: 1, top: 0 },
  entering: { opacity: 0, top: '100vh' },
}

class MainMenu extends React.PureComponent {
  constructor(props) {
    super(props)
    const { dispatch } = props
    this.actions = bindActionCreators({ requestData }, dispatch)
  }

  onSignOutClick = () => {
    const { history } = this.props
    this.actions.requestData('GET', 'users/signout', {
      handleSuccess: () => {
        history.push('/connexion')
        this.toggleMainMenu()
      },
    })
  }

  toggleMainMenu = () => {
    const { dispatch } = this.props
    dispatch(toggleMainMenu())
  }

  renderLogOutLink() {
    return (
      <button
        type="button"
        id="main-menu-logout-button"
        className="pc-text-button flex-columns text-left p16"
        onClick={this.onSignOutClick}
      >
        <span className="menu-icon">
          <Icon svg="ico-deconnect-w" alt="" />
        </span>
        <span>Déconnexion</span>
      </button>
    )
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

  render() {
    const { isVisible, user } = this.props
    return (
      <Transition in={isVisible} timeout={transitionDelay}>
        {state => (
          <div
            id="main-menu"
            className="is-overlay p12"
            style={{ ...defaultStyle, ...transitionStyles[state] }}
          >
            <div className="inner is-relative is-clipped flex-rows flex-end">
              {this.renderCloseButton()}
              <Scrollbars autoHide>
                <div className="scroll-container pc-theme-red">
                  <MenuHeader user={user} />
                  <nav id="main-menu-navigation" className="flex-rows mt16 pb0">
                    {menuitems &&
                      menuitems.map(
                        obj =>
                          obj && (
                            <MenuLink
                              key={obj.path || obj.href}
                              item={obj}
                              clickHandler={this.toggleMainMenu}
                            />
                          )
                      )}
                    {this.renderLogOutLink()}
                  </nav>
                </div>
              </Scrollbars>
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
  history: PropTypes.object.isRequired,
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
