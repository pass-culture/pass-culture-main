// Warning: this component is volontarily impure.
// Don't use it as an example unless you know what you are doing.

import React, { Component } from 'react'
import { connect } from 'react-redux'
import moment from 'moment'
import get from 'lodash.get'

import { showModal } from '../../reducers/modal'

import '../../utils/debugInitializer'

class Debug extends Component {

  static defaultProps = {
    timeoutDuration: 3000,
  }

  showDebug = () => {
    this.props.showModal(
      (<div className='debug-modal'>
        <h1 className='title'>Pass Culture Debug</h1>
        <pre>{get(window, 'logContent', []).map(this.renderLine)}</pre>
      </div>), {
      fullscreen: true,
      maskColor: 'transparent',
    })
  }

  handleTouchPress = (e) => {
    if (get(e, 'touches', []).length >= 3) {
      this.buttonPressTimer = setTimeout(() => {
        this.showDebug()
      }, this.props.timeoutDuration);
    }
  }

  handleTouchRelease = () => {
    clearTimeout(this.buttonPressTimer);
  }

  displayVariable = value => {
    if (typeof value === 'string') return value;
    return JSON.stringify(value, null, 2)
      .replace(/"([^(")"]+)":/g,"$1:") // remove quotes
  }

  renderLine = ({time, method, hash, values}) => {
    return (
      <code key={hash} title={time}>
        <div className='header'>{`${method.toUpperCase()} | `}
        <time dateTime={time}>{moment(time).format('h:mm:ss')}</time></div>
        <div className='log'>{values.map(this.displayVariable).join('\n')}</div>
      </code>
    )
  }

  render() {
    return <div
      className={this.props.className}
      onTouchStart={this.handleTouchPress}
      onTouchEnd={this.handleTouchRelease}
      onClick={e => (e.detail === 3 && e.shiftKey) && this.showDebug(e)}
      >
      {this.props.children} />
    </div>
  }
}
export default connect(state => ({}), {
  showModal,
})(Debug)
