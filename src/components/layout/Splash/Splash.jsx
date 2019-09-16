import PropTypes from 'prop-types'
import React from 'react'
import { Transition } from 'react-transition-group'
import { bindActionCreators } from 'redux'

import Icon from '../Icon/Icon'
import { closeSplash } from '../../../reducers/splash'

const duration = 1000

const defaultStyle = {
  opacity: 0,
  transition: `opacity ${duration}ms ease-in-out`,
}

const transitionStyles = {
  entered: { opacity: 1 },
  entering: { opacity: 0 },
}

class Splash extends React.PureComponent {
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
            className="pc-gradient is-overlay text-center"
            id="splash"
            style={{ ...defaultStyle, ...transitionStyles[state] }}
          >
            <Icon
              alt="Logo pass Culture"
              svg="logo-group"
            />
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
