import React, { Component, Fragment } from 'react'
import { NavLink } from 'react-router-dom'
import get from 'lodash.get'
import { connect } from 'react-redux'
import { Icon, requestData } from 'pass-culture-shared'
import Delete from './Delete'

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

  componentDidMount() {
    this.props.onRef(this.$submit)
  }

  render() {
    const {
      isEditing,
      offer,
      isStockOnly,
      stockPatch,
      eventOccurrencePatch,
    } = this.props

    if (isEditing) {
      return (
        <Fragment>
          <td className="is-clipped">
            <NavLink
              className="button is-secondary is-small"
              to={`/offres/${get(offer, 'id')}?gestion`}>
              Annuler
            </NavLink>
          </td>
          <td ref={_e => (this.$submit = _e)} />
        </Fragment>
      )
    }

    return (
      <Fragment>
        <td className="is-clipped">
          {!this.state.isDeleting && (
            <button
              className="button is-small is-secondary"
              style={{ width: '100%' }}
              onClick={this.onDeleteClick}>
              <span className="icon">
                <Icon svg="ico-close-r" />
              </span>
            </button>
          )}

          {this.state.isDeleting && (
            <Delete
              eventOccurrencePatch={eventOccurrencePatch}
              isStockOnly={isStockOnly}
              stockPatch={stockPatch}
              onCancelDeleteClick={this.onCancelDeleteClick}
              onConfirmDeleteClick={this.onConfirmDeleteClick}
            />
          )}
        </td>
        <td ref={_e => (this.$submit = _e)}>
          {!this.state.isDeleting && (
            <NavLink
              to={`/offres/${get(offer, 'id')}?gestion&${
                isStockOnly
                  ? `stock=${get(stockPatch, 'id')}`
                  : `date=${get(eventOccurrencePatch, 'id')}`
              }`}
              className="button is-small is-secondary">
              <span className="icon">
                <Icon svg="ico-pen-r" />
              </span>
            </NavLink>
          )}
        </td>
      </Fragment>
    )
  }
}

export default connect()(Actions)
