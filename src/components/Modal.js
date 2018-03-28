import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { closeModal } from '../reducers/modal'
import Icon from './Icon'

class Modal extends Component {

  constructor() {
    super()
    this.state = {
      outside: true,
    }
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.isActive && !this.props.isActive) {
      if (nextProps.isActive) {
        this.openTimeout = setTimeout(() => {
          this.setState({
            outside: false
          })
        }, 0)
      } else {

      }
    }
  }

  onCloseClick = () => {
    if (this.props.isUnclosable) return;
    this.setState({
      outside: true,
    })
    this.closeTimeout = setTimeout(() => {
      const { closeModal, onCloseClick } = this.props
      onCloseClick && onCloseClick()
      closeModal()
    }, this.props.transitionDuration)

  }

  stopPropagation(e) {
    e.nativeEvent.stopImmediatePropagation() // Prevent click bubbling and closing modal
    e.stopPropagation()
  }

  componentWillUnmount() {
    this.openTimeout && clearTimeout(this.openTimeout);
    this.closeTimeout && clearTimeout(this.closeTimeout);
  }

  transitionRelativePosition() {
    if (!this.state.outside) return {top: 0, left: 0};
    switch(this.props.fromDirection) {
      case 'top':
        return {top: '-100%'}
      case 'bottom':
        return {top: '100%'}
      case 'left':
        return {left: '-100%'}
      case 'right':
        return {right: '100%'}
      default:
        return {};
    }
  }

  render () {
    const { ContentComponent,
      isActive,
      hasCloseButton,
    } = this.props
    return (
      <div className={classnames('modal', {
        'active': isActive,
      })}
        role='dialog'
        onClick={this.onCloseClick}>
        <div
          className={classnames('modal-dialog', {
            fullscreen: this.props.fullscreen
          })}
          role='document'
          style={Object.assign({transitionDuration: `${this.props.transitionDuration}ms` }, this.transitionRelativePosition())}
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
  fromDirection: 'bottom'
}

export default connect(({ modal: { config, ContentComponent, isActive } }) =>
  Object.assign({ ContentComponent, isActive }, config),
  { closeModal }
)(Modal)
