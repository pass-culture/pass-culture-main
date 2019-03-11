import { Icon } from 'pass-culture-shared'
import React, { Component, Fragment } from 'react'
import { NavLink } from 'react-router-dom'
import { Portal } from 'react-portal'
import get from 'lodash.get'
import { connect } from 'react-redux'
import { requestData } from 'redux-saga-data'

import DeleteDialog from './DeleteDialog'

class EditAndDeleteActions extends Component {
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
    const {
      dispatch,
      eventOccurrencePatch,
      isStockOnly,
      stockPatch,
    } = this.props
    dispatch(
      requestData({
        apiPath: isStockOnly
          ? `stocks/${stockPatch.id}`
          : `eventOccurrences/${eventOccurrencePatch.id}`,
        method: 'DELETE',
      })
    )
  }

  render() {
    const { offer, isStockOnly, stockPatch, eventOccurrencePatch } = this.props

    const editAndDeleteNavUrl = `/offres/${get(offer, 'id')}?gestion&${
      isStockOnly
        ? `stock=${get(stockPatch, 'id')}`
        : `date=${get(eventOccurrencePatch, 'id')}`
    }`

    // Delete dialog
    if (this.state.isDeleting) {
      return (
        <td colSpan="2">
          <Portal node={this.props.tbody}>
            <DeleteDialog
              isStockOnly={isStockOnly}
              onCancelDeleteClick={this.onCancelDeleteClick}
              onConfirmDeleteClick={this.onConfirmDeleteClick}
            />
          </Portal>
        </td>
      )
    }

    // Delete and edit buttons
    return (
      <Fragment>
        <td>
          <NavLink
            to={editAndDeleteNavUrl}
            className="button is-small is-secondary edit-stock">
            <span className="icon">
              <Icon svg="ico-pen-r" />
            </span>
          </NavLink>
        </td>
        <td className="is-clipped">
          {!this.state.isDeleting && (
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

export default connect()(EditAndDeleteActions)
