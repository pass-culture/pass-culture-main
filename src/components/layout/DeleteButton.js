import React, { Component } from 'react'
import { connect } from 'react-redux'

import Icon from './Icon'
import { closeModal, showModal } from '../../reducers/modal'
import { requestData } from '../../reducers/data'

class DeleteButton extends Component {
  onCancelClick = () => {
    this.props.closeModal()
  }
  onConfirmClick = () => {
    const { collectionName, id, requestData } = this.props
    requestData('DELETE', `/${collectionName}?id:${id}`)
  }
  render() {
    const { className, disabled, showModal, text } = this.props
    return (
      <button
        className={className}
        disabled={disabled}
        onClick={() =>
          showModal(
            <div>
              <div className="mb2">Enlever ?</div>
              <button
                className="button is-default"
                onClick={this.onConfirmClick}
              >
                Oui
              </button>
              <button
                className="button is-default"
                onClick={this.onCancelClick}
              >
                Non
              </button>
            </div>
          )
        }
      >
        {text || <Icon name="delete" />}
      </button>
    )
  }
}

export default connect(null, { closeModal, requestData, showModal })(
  DeleteButton
)
