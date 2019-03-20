import get from 'lodash.get'
import PropTypes from 'prop-types'
import { Icon } from 'pass-culture-shared'
import React, { Component, Fragment } from 'react'
import { Portal } from 'react-portal'
import { NavLink } from 'react-router-dom'
import { requestData } from 'redux-saga-data'

import DeleteDialog from './DeleteDialog'

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
    const { offer, isEventStock, stockPatch } = this.props
    const { id: offerId } = offer || {}
    const { isDeleting } = this.state

    const editAndDeleteNavUrl = `/offres/${offerId}?gestion&stock=${get(
      stockPatch,
      'id'
    )}`

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
          <NavLink
            to={editAndDeleteNavUrl}
            className="button is-small is-secondary edit-stock">
            <span className="icon">
              <Icon svg="ico-pen-r" />
            </span>
          </NavLink>
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
}

export default EditAndDeleteControl
