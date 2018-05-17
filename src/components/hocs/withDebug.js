import React, { Component } from 'react'
import { connect } from 'react-redux'
import moment from 'moment'

import { showModal } from '../../reducers/modal'

import { debug, log, warn, error } from '../../reducers/log'

const withDebug = WrappedComponent => {
  class _withDebug extends Component {

    constructor(props) {
      super(props)
      window.debug = this.props.debug;
      window.log = this.props.log;
      window.warn = this.props.warn;
      window.error = this.props.error;
    }

    static defaultProps = {
      timeoutDuration: 3000,
    }

    showDebug = () => {
      this.props.showModal(
        (<div className='debug-modal'>
          <h1 className='title'>Debug</h1>
          <pre>{this.props.logContent.map(({time, method, ...values}) => <code title={time}>{`${method.toUpperCase()}: ${values.join(' - ')}`}</code>)}</pre>
        </div>), {
        fullscreen: true,
        maskColor: 'transparent',
      })
    }

    handleTouchPress = () => {
      this.buttonPressTimer = setTimeout(() => {
        this.showDebug()
      }, this.props.timeoutDuration);
    }

    handleTouchRelease = () => {
      clearTimeout(this.buttonPressTimer);
    }

    render() {
      return <div
        onTouchStart={e => (e.touches && e.touches.length > 1 || e.shiftKey) && this.handleTouchPress()}
        onTouchEnd={this.handleTouchRelease}
        onClick={e => (e.detail === 3) && this.showDebug(e)}
        style={{height: 'inherit', width: 'inherit'}}
        >
        <WrappedComponent {...this.props} />
      </div>
    }
  }
  return connect(state => ({
    logContent: state.log
  }), {
    showModal,
    debug,
    log,
    warn,
    error,
  })(_withDebug)
}

export default withDebug