import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { closeModal } from '../reducers/modal'
import Icon from './Icon'

class Modal extends Component {

  constructor() {
    super()
    this.state = {
      translate: true,
      display: false,
    }
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.isActive && !this.props.isActive) {
      // Opening
      this.setState({
        display: true,
      })
      this.openTimeout = setTimeout(() => {
        this.setState({
          translate: false,
        })
      }, 0)
    } else if (!nextProps.isActive && this.props.isActive) {
      // Closing
      this.setState({
        translate: true,
      })
      this.closeTimeout = setTimeout(() => {
        this.setState({
          display: false,
        })
      }, this.props.transitionDuration)

    }
  }

  onCloseClick = () => {
    if (this.props.isUnclosable) return;
    const { closeModal, onCloseClick } = this.props
    onCloseClick && onCloseClick()
    closeModal()
  }

  stopPropagation(e) {
    e.nativeEvent.stopImmediatePropagation() // Prevent click bubbling and closing modal
    e.stopPropagation()
  }

  componentWillUnmount() {
    this.openTimeout && clearTimeout(this.openTimeout);
    this.closeTimeout && clearTimeout(this.closeTimeout);
  }

  transform() {
    if (!this.state.translate) return '';
    switch(this.props.fromDirection) {
      case 'top':
        return 'translate(0, -100vh)'
      case 'bottom':
        return 'translate(0, 100vh)'
      case 'left':
        return 'translate(-100vw, 0)'
      case 'right':
        return 'translate(100vw, 0)'
      default:
        return {};
    }
  }

  render () {
    const {
      ContentComponent,
      hasCloseButton,
      maskColor,
      transitionDuration,
    } = this.props
    return (
      <div className={classnames('modal', {
        'active': this.state.display,
      })}
        role='dialog'
        style={{backgroundColor: maskColor}}
        onClick={this.onCloseClick}>
        <div
          className={classnames('modal-dialog', {
            fullscreen: this.props.fullscreen
          })}
          role='document'
          style={{transitionDuration: `${transitionDuration}ms`, transform: this.transform() }}
          onClick={e => this.stopPropagation(e)}>
          { hasCloseButton && (
              <button
                className='close-button'
                onClick={this.onCloseClick} >
                <Icon svg='ico-close' />
              </button>
          )}
          <div className='modal-content'>
            { ContentComponent && <ContentComponent /> }
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
  maskColor: 'rgba(0, 0, 0, 0.8)'
}

export default connect(({ modal: { config, ContentComponent, isActive } }) =>
  Object.assign({ ContentComponent, isActive }, config),
  { closeModal }
)(Modal)
