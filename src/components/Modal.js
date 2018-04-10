import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { closeModal } from '../reducers/modal'
import Icon from './Icon'

const initialState = {
  translate: true,
  display: false,
}

class Modal extends Component {

  constructor() {
    super()
    this.state = initialState
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
      }, this.props.transitionDuration)
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

  onCloseClick = e => {
    if (this.props.isUnclosable || !this.props.isActive) return;
    const { closeModal, onCloseClick } = this.props
    onCloseClick && onCloseClick()
    closeModal()
    e.preventDefault()
  }

  stopPropagation(e) {
    e.nativeEvent.stopImmediatePropagation() // Prevent click bubbling and closing modal
    e.stopPropagation()
  }

  componentDidMount() {
    document.addEventListener('backbutton', this.onCloseClick)
  }

  componentWillUnmount() {
    this.openTimeout && clearTimeout(this.openTimeout);
    this.closeTimeout && clearTimeout(this.closeTimeout);
    document.removeEventListener('backbutton', this.onCloseClick)
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
      isUnclosable,
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
          style={{
            transitionDuration: `${transitionDuration}ms`,
            transform: this.transform()
          }}
          onClick={e => this.stopPropagation(e)}>
          { !isUnclosable && hasCloseButton && (
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
  { closeModal })
(Modal)