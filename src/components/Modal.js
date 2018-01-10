import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { closeModal } from '../reducers/modal'

class Modal extends Component {
  onCloseClick = () => {
    this.props.closeModal()
  }
  render () {
    const { content,
      isActive
    } = this.props
    const classes = classnames({
      'modal--active': isActive
    }, 'modal')
    return (
      <div className={classes}
        role='dialog'
        onClick={this.onCloseClick}>
        <div className='modal__dialog'
          role='document'
          onClick={e => {
            e.nativeEvent.stopImmediatePropagation() // Prevent click bubbling and closing modal
            e.stopPropagation()
          }}>
          <div className='modal__content'>
            {content}
          </div>
        </div>
      </div>
    )
  }
}

export default connect(({ modal: { content, isActive } }) =>
  ({ content, isActive }),
  { closeModal })(Modal)
