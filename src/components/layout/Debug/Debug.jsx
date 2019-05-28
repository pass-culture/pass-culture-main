// Warning: this component is volontarily impure.
// Don't use it as an example unless you know what you are doing.
import moment from 'moment'
import get from 'lodash.get'
import PropTypes from 'prop-types'
import React from 'react'

import '../../../utils/debugInitializer'

class Debug extends React.PureComponent {
  showDebug = () => {
    const { dispatchShowModal } = this.props
    dispatchShowModal(
      <div className="debug-modal">
        <h1 className="title">
          {'Pass Culture Debug'}
        </h1>
        <pre>
          {get(window, 'logContent', []).map(this.renderLine)}
        </pre>
      </div>,
      {
        fullscreen: true,
        maskColor: 'transparent',
      }
    )
  }

  handleTouchPress = e => {
    const isTouched = get(e, 'touches', []).length >= 2
    if (!isTouched) return
    const { timeoutDuration } = this.props
    this.buttonPressTimer = setTimeout(() => {
      this.showDebug()
    }, timeoutDuration)
  }

  handleTouchRelease = () => {
    clearTimeout(this.buttonPressTimer)
  }

  displayVariable = value => {
    if (typeof value === 'string') return value
    return JSON.stringify(value, null, 2).replace(/"([^(")"]+)":/g, '$1:') // remove quotes
  }

  renderLine = ({ time, method, hash, values }) => (
    <code key={hash} title={time}>
      <div className="header">
        {`${method.toUpperCase()} | `}
        <time dateTime={time}>
          {moment(time).format('h:mm:ss')}
        </time>
      </div>
      <div className="log">
        {values.map(this.displayVariable).join('\n')}
      </div>
    </code>
  )

  render() {
    const { children, className } = this.props
    return (
      // NOTE: c'est quoi le comportement attendu par ce composant
      // actuellement il sert de container
      // or sur des raisons d'accessibilité il n'est pas valide
      // FIXME: ce composant doit être remplacé
      // eslint-disable-next-line
      <div
        className={className}
        onTouchStart={this.handleTouchPress}
        onTouchEnd={this.handleTouchRelease}
        onClick={e => e.detail === 3 && e.shiftKey && this.showDebug(e)}
      >
        {children}
      </div>
    )
  }
}

Debug.defaultProps = {
  className: '',
  timeoutDuration: 3000,
}

Debug.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
  dispatchShowModal: PropTypes.func.isRequired,
  timeoutDuration: PropTypes.number,
}

export default Debug
