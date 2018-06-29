import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'

import Icon from './Icon'
import { closeModal } from '../../reducers/modal'

const initialState = {
  translate: true,
  display: false,
}

class Modal extends Component {
  constructor() {
    super()
    this.state = initialState
  }

  handleActiveChange = (prevProps = {}) => {
    const {
      isActive,
      transitionDuration
    } = this.props

    if (isActive && !prevProps.isActive) {
      // Opening
      this.setState({
        display: true,
      })
      this.openTimeout = setTimeout(() => {
        this.setState({
          translate: false,
        })
      }, transitionDuration)
      document.addEventListener('backbutton', this.onCloseClick)
    } else if (!isActive && prevProps.isActive) {
      // Closing
      this.setState({
        translate: true,
      })
      this.closeTimeout = setTimeout(() => {
        this.setState({
          display: false,
        })
      }, transitionDuration)
      document.removeEventListener('backbutton', this.onCloseClick)
    }
  }

  onCloseClick = e => {
    if (this.props.isUnclosable || !this.props.isActive) return true
    const { closeModal, onCloseClick } = this.props
    onCloseClick && onCloseClick()
    closeModal()
    e.preventDefault()
  }

  stopPropagation(e) {
    e.nativeEvent.stopImmediatePropagation() // Prevent click bubbling and closing modal
    e.stopPropagation()
  }

  transform() {
    if (!this.state.translate) return ''
    switch (this.props.fromDirection) {
      case 'top':
        return 'translate(0, -100vh)'
      case 'bottom':
        return 'translate(0, 100vh)'
      case 'left':
        return 'translate(-100vw, 0)'
      case 'right':
        return 'translate(100vw, 0)'
      default:
        return {}
    }
  }

  componentDidMount() {
    this.handleActiveChange()
  }

  componentDidUpdate (prevProps) {
    const {
      closeModal,
      isClosingOnLocationChange,
      location: { pathname }
    } = this.props
    if (isClosingOnLocationChange && pathname !== prevProps.location.pathname) {
      closeModal()
    }

    this.handleActiveChange(prevProps)
  }

  componentWillUnmount() {
    this.openTimeout && clearTimeout(this.openTimeout)
    this.closeTimeout && clearTimeout(this.closeTimeout)
  }

  render() {
    const {
      fullscreen,
      hasCloseButton,
      isUnclosable,
      maskColor,
      $modal,
      transitionDuration,
    } = this.props
    return (
      <div
        className={classnames('modal', {
          active: this.state.display,
        })}
        role="dialog"
        style={{ backgroundColor: maskColor }}
        onClick={this.onCloseClick}
      >
        <div
          className={classnames('modal-dialog', {
            fullscreen,
          })}
          role="document"
          style={{
            transitionDuration: `${transitionDuration}ms`,
            transform: this.transform(),
          }}
          onClick={e => this.stopPropagation(e)}
        >
          {!isUnclosable &&
            hasCloseButton && (
              <button className="close" onClick={this.onCloseClick}>
                <Icon svg="ico-close-b" />
              </button>
            )}
          <div className="modal-content">
            {$modal}
          </div>
        </div>
      </div>
    )
  }
}

Modal.defaultProps = {
  transitionDuration: 250,
  hasCloseButton: true,
  fromDirection: 'bottom',
  maskColor: 'rgba(0, 0, 0, 0.8)',
}

export default  withRouter(connect(
  ({ modal: { config, $modal, isActive } }) =>
    Object.assign({ $modal, isActive }, config),
  { closeModal }
)(Modal))
