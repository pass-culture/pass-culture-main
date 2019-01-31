/* eslint
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { Transition } from 'react-transition-group'
import { withRouter } from 'react-router-dom'

import routes from '../../utils/routes'
import MenuItem from './MenuItem'
import MenuHeader from './MenuHeader'
import MenuSignoutButton from './MenuSignoutButton'
import { toggleOverlay } from '../../reducers/overlay'
import { getMainMenuItems } from '../../utils/routes-utils'

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
  componentDidMount() {
    const { dispatch } = this.props
    dispatch(toggleOverlay())
  }

  componentWillUnmount() {
    const { dispatch } = this.props
    dispatch(toggleOverlay())
  }

  toggleMainMenu = () => {
    const { history } = this.props
    history.goBack()
  }

  renderCloseButton = () => (
    <button
      type="button"
      id="main-menu-close-button"
      className="pc-text-button is-white-text is-absolute fs16"
      onClick={() => this.toggleMainMenu()}
    >
      <span
        aria-hidden
        className="icon-legacy-close"
        title="Fermer la navigation"
      />
    </button>
  )

  renderNavigationLinks = () => (
    <React.Fragment>
      {menuitems &&
        menuitems.map(
          obj => obj && <MenuItem item={obj} key={obj.path || obj.href} />
        )}
      <MenuSignoutButton />
    </React.Fragment>
  )

  render() {
    const { isVisible, user } = this.props
    return (
      <Transition in={isVisible} timeout={transitionDelay}>
        {status => (
          <div
            id="main-menu"
            className={`is-overlay ${status}`}
            style={{ ...defaultStyle, ...transitionStyles[status] }}
          >
            <div className="inner is-full-layout is-relative flex-rows flex-end">
              <div className="pc-scroll-container">
                <div
                  id="main-menu-fixed-container"
                  className="pc-theme-red is-relative"
                >
                  {this.renderCloseButton()}
                  <MenuHeader
                    user={user}
                    toggleMainMenu={this.toggleMainMenu}
                  />
                  <nav id="main-menu-navigation" className="flex-rows mt16 pb0">
                    {this.renderNavigationLinks()}
                  </nav>
                </div>
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
  history: PropTypes.object.isRequired,
  isVisible: PropTypes.bool.isRequired,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]),
}

const mapStateToProps = state => ({
  isVisible: true,
  user: state.user,
})

export default compose(
  withRouter,
  connect(mapStateToProps)
)(MainMenu)
