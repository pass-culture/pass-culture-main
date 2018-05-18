// Warning: this component is volontarily impure.
// Don't use it as an example unless you know what you are doing.

import React, { Component } from 'react'
import { connect } from 'react-redux'
import moment from 'moment'
import get from 'lodash.get'

import { showModal } from '../../reducers/modal'
import { randomHash } from '../../utils/random'

const withDebug = WrappedComponent => {
  class _withDebug extends Component {

    constructor(props) {
      super(props)
      window.debug = this.debug;
      window.log = this.log;
      window.warn = this.warn;
      window.error = this.error;
      window.logContent = [];
      console.debug('Debug component started')
    }

    static defaultProps = {
      logLength: 100,
      timeoutDuration: 3000,
    }

    appendToLog({method, values}) {
      console[method](...values)
      window.logContent = window.logContent.slice(-this.props.logLength).concat([{
          method,
          values,
          time: new Date(),
          hash: randomHash(),
        }])
    }

    debug = (...values) => {
      this.appendToLog({
        method: 'debug',
        values,
      })
    }
    log = (...values) => {
      this.appendToLog({
        method: 'log',
        values,
      })
    }

    warn = (...values) => {
      this.appendToLog({
        method: 'warn',
        values,
      })
    }
    error = (...values) => {
      this.appendToLog({
        method: 'error',
        values,
      })
    }

    showDebug = () => {
      this.props.showModal(
        (<div className='debug-modal'>
          <h1 className='title'>Pass Culture Debug</h1>
          <pre>{window.logContent.map(this.renderLine)}</pre>
        </div>), {
        fullscreen: true,
        maskColor: 'transparent',
      })
    }

    handleTouchPress = (e) => {
      if (get(e, 'touches', []).length > 1 || e.shiftKey) {
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
        onTouchStart={this.handleTouchPress}
        onTouchEnd={this.handleTouchRelease}
        onClick={e => (e.detail === 3) && this.showDebug(e)}
        style={{height: 'inherit', width: 'inherit'}}
        >
        <WrappedComponent {...this.props} />
      </div>
    }
  }
  return connect(state => ({}), {
    showModal,
  })(_withDebug)
}

export default withDebug