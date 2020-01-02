import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Transition } from 'react-transition-group'
import { bindActionCreators } from 'redux'
import { closeSplash } from '../../../reducers/splash'

import Icon from '../Icon/Icon'

const duration = 1000

const defaultStyle = {
  opacity: 0,
  transition: `opacity ${duration}ms ease-in-out`,
}

const transitionStyles = {
  entered: { opacity: 1 },
  entering: { opacity: 0 },
}

class Splash extends PureComponent {
  constructor(props) {
    super(props)
    this.state = { close: !props.isBetaPage }
    this.actions = bindActionCreators({ closeSplash }, props.dispatch)
  }

  componentDidMount() {
    const { closeTimeout, isBetaPage } = this.props
    const delay = isBetaPage ? closeTimeout : 1
    setTimeout(() => this.setState({ close: true }, this.actions.closeSplash), delay)
  }

  render() {
    const { close } = this.state
    return (
      <Transition
        in={!close}
        timeout={duration}
        unmountOnExit
      >
        {state => (
          <div
            className="is-overlay text-center"
            id="splash"
            style={{ ...defaultStyle, ...transitionStyles[state] }}
          >
            <Icon
              alt="Logo pass Culture"
              svg="logo-group"
            />
            <span id="beta-mention">
              {'beta'}
            </span>
          </div>
        )}
      </Transition>
    )
  }
}

Splash.propTypes = {
  closeTimeout: PropTypes.number.isRequired,
  dispatch: PropTypes.func.isRequired,
  isBetaPage: PropTypes.bool.isRequired,
}

export default Splash
