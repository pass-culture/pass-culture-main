import React, { Component } from 'react'
import { connect } from 'react-redux'

import { showModal } from '../../reducers/modal'

import Debug from '../layout/Debug'

const withDebug = WrappedComponent => {
  class _withDebug extends Component {

    static defaultProps = {
      timeoutDuration: 3000,
    }

    constructor(props) {
      super(props)
      this.state = {
        log: '',
      }
    }

    componentDidMount() {
      const nativeConsole = console.log;
      console = {};
      console.log = (args) => {
        this.setState({
          log: this.state + '\n' + args
        })
        nativeConsole(args);
      };
      window.console = console;
      console.log('console plugged')
    }

    onLongPress = () => {
      this.props.showModal(<Debug log={this.state.log} />, {
        fullscreen: true,
        maskColor: 'transparent',
      })
    }

    handleButtonPress = (e) => {
      if ((e.touches && e.touches.length > 1) || e.shiftKey) {
        this.buttonPressTimer = setTimeout(this.onLongPress, this.props.timeoutDuration);
      }
    }

    handleButtonRelease = () => {
      clearTimeout(this.buttonPressTimer);
    }

    render() {
      return <div
        onTouchStart={this.handleButtonPress}
        onTouchEnd={this.handleButtonRelease}
        onMouseDown={this.handleButtonPress}
        onMouseUp={this.handleButtonRelease}
        style={{height: 'inherit', width: 'inherit'}}
        >
        <WrappedComponent {...this.props} />
      </div>
    }
  }
  return connect(() => ({}), {
    showModal
  })(_withDebug)
}

export default withDebug