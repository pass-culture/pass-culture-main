import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from './Icon'
import { closeModal, showModal } from '../reducers/modal'
import { requestData } from '../reducers/data'

class DeleteButton extends Component {
  onCancelClick = () => {
    this.props.closeModal()
  }
  onConfirmClick = () => {
    const { collectionName, id, requestData } = this.props
    requestData('DELETE', `/${collectionName}?id:${id}`)
  }
  render () {
    const { className, disabled, showModal, text } = this.props
    return (
      <button className={className || 'button button--alive'}
        onClick={() => showModal(
          <div>
            <div className='mb2'>
              Enlever cette offre ?
            </div>
            <button className='button button--alive mr2'
              disabled
              onClick={this.onConfirmClick}
            >
              Oui
            </button>
            <button className='button button--alive'
              onClick={this.onCancelClick}
            >
              Non
            </button>
          </div>
        )}
      >
        { text || <Icon name='delete' /> }
      </button>
    )
  }
}

export default connect(
  null,
  { closeModal, requestData, showModal }
)(DeleteButton)
