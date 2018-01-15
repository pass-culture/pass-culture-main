import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { closeModal } from '../reducers/modal'

class Modal extends Component {
  onCloseClick = () => {
    this.props.closeModal()
  }
  render () {
    const { ContentComponent,
      isActive
    } = this.props
    return (
      <div className={classnames({
        'modal--active': isActive
      }, 'modal')}
        role='dialog'
        onClick={this.onCloseClick}>
        <div className='modal__dialog relative'
          role='document'
          onClick={e => {
            e.nativeEvent.stopImmediatePropagation() // Prevent click bubbling and closing modal
            e.stopPropagation()
          }}>
          <button className='button button--alive button--rounded absolute top-0 right-0 mt2 mr2'
            onClick={this.onCloseClick}
          >
            x
          </button>
          <div className='modal__content'>
            { ContentComponent && <ContentComponent /> }
          </div>
        </div>
      </div>
    )
  }
}

export default connect(({ modal: { ContentComponent, isActive } }) =>
  ({ ContentComponent, isActive }),
  { closeModal })(Modal)
