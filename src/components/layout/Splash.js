import PropTypes from 'prop-types'
import { Icon } from 'pass-culture-shared'
import React from 'react'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { Transition } from 'react-transition-group'
import { closeSplash } from '../../reducers/splash'

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
    setTimeout(
      () => this.setState({ close: true }, this.actions.closeSplash),
      delay
    )
  }

  render() {
    const { close } = this.state
    return (
      <Transition unmountOnExit in={!close} timeout={duration}>
        {state => (
          <div
            id="splash"
            className="is-overlay has-text-centered"
            style={{ ...defaultStyle, ...transitionStyles[state] }}
          >
            <Icon svg="logo-group" alt="Logo Pass Culture" />
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

const mapStateToProps = ({ splash: { closeTimeout, isActive } }) => ({
  closeTimeout,
  isBetaPage: isActive,
})

export default connect(mapStateToProps)(Splash)
