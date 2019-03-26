import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import { Portal } from 'react-portal'
import { requestData } from 'redux-saga-data'

import DeleteDialog from './DeleteDialog'
import { withFrenchQueryRouter } from 'components/hocs'
import Icon from 'components/layout/Icon'

class EditAndDeleteControl extends Component {
  constructor(props) {
    super(props)
    this.state = {
      isDeleting: false,
    }
  }

  onDeleteClick = () => {
    this.setState({ isDeleting: true })
  }

  onCancelDeleteClick = () => {
    this.setState({ isDeleting: false })
  }

  onConfirmDeleteClick = () => {
    const { dispatch, stockPatch } = this.props
    dispatch(
      requestData({
        apiPath: `stocks/${stockPatch.id}`,
        method: 'DELETE',
      })
    )
  }

  render() {
    const { isEventStock, query, stockPatch } = this.props
    const { id: stockId } = stockPatch
    const { isDeleting } = this.state

    if (!stockId) {
      return null
    }

    // Delete dialog
    if (isDeleting) {
      return (
        <td colSpan="2">
          <Portal node={this.props.tbody}>
            <DeleteDialog
              isEventStock={isEventStock}
              onCancelDeleteClick={this.onCancelDeleteClick}
              onConfirmDeleteClick={this.onConfirmDeleteClick}
            />
          </Portal>
        </td>
      )
    }

    return (
      <Fragment>
        <td>
          <button
            className="button is-small is-secondary edit-stock"
            id={`edit-stock-${stockId}-button`}
            onClick={() => query.changeToModificationUrl('stock', stockId)}>
            <span className="icon">
              <Icon svg="ico-pen-r" />
            </span>
          </button>
        </td>
        <td className="is-clipped">
          {!isDeleting && (
            <button
              className="button is-small is-secondary delete-stock"
              style={{ width: '100%' }}
              onClick={this.onDeleteClick}>
              <span className="icon">
                <Icon svg="ico-close-r" />
              </span>
            </button>
          )}
        </td>
      </Fragment>
    )
  }
}

EditAndDeleteControl.propTypes = {
  dispatch: PropTypes.func.isRequired,
  isEventStock: PropTypes.bool.isRequired,
  query: PropTypes.object.isRequired,
}

export default withFrenchQueryRouter(EditAndDeleteControl)
