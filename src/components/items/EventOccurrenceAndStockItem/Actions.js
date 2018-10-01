import React, { Component, Fragment } from 'react'
import { NavLink } from 'react-router-dom'
import get from 'lodash.get'
import { Icon } from 'pass-culture-shared'

class Actions extends Component {
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
      onDeleteClick,
    } = this.props

    return (
      <Fragment>
        <td className="is-clipped">
          {isEditing ? (
            <NavLink
              className="button is-secondary is-small"
              to={`/offres/${get(offer, 'id')}?gestion`}>
              Annuler
            </NavLink>
          ) : (
            <button
              className="button is-small is-secondary"
              style={{ width: '100%' }}
              onClick={onDeleteClick}>
              <span className="icon">
                <Icon svg="ico-close-r" />
              </span>
            </button>
          )}
        </td>
        <td ref={_e => (this.$submit = _e)}>
          {!isEditing && (
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

export default Actions
