import React, { Component, Fragment } from 'react'
import { NavLink } from 'react-router-dom'
import { Portal } from 'react-portal'
import get from 'lodash.get'
import { connect } from 'react-redux'
import { Icon, requestData } from 'pass-culture-shared'
import DeleteDialog from './DeleteDialog'

class Actions extends Component {
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
      requestData(
        'DELETE',
        isStockOnly
          ? `stocks/${stockPatch.id}`
          : `eventOccurrences/${eventOccurrencePatch.id}`
      )
    )
  }

  render() {
    const { offer, isStockOnly, stockPatch, eventOccurrencePatch } = this.props

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
            to={`/offres/${get(offer, 'id')}?gestion&${
              isStockOnly
                ? `stock=${get(stockPatch, 'id')}`
                : `date=${get(eventOccurrencePatch, 'id')}`
            }`}
            className="button is-small is-secondary editStock">
            <span className="icon">
              <Icon svg="ico-pen-r" />
            </span>
          </NavLink>
        </td>
        <td className="is-clipped">
          {!this.state.isDeleting && (
            <button
              className="button is-small is-secondary deleteStock"
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

export default connect()(Actions)
