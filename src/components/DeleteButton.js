import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from './Icon'
import { closeModal, showModal } from '../reducers/modal'
import { requestData } from '../reducers/request'

class DeleteButton extends Component {
  onCancelClick = () => {
    this.props.closeModal()
  }
  onConfirmClick = () => {
    const { collectionName, id, requestData } = this.props
    requestData('DELETE', `/${collectionName}?id:${id}`)
  }
  render () {
    return (
      <button className='button button--alive'
        onClick={() => this.props.showModal(
          <div>
            <div className='mb2'>
              Enlever cette offre ?
            </div>
            <button className='button button--alive mr2'
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
        <Icon name='delete' />
      </button>
    )
  }
}

export default connect(
  null,
  { closeModal, requestData, showModal }
)(DeleteButton)
