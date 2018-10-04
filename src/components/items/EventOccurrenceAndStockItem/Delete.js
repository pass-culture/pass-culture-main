import React, { Component } from 'react'

class Delete extends Component {
  render() {
    const {
      isStockOnly,
      onCancelDeleteClick,
      onConfirmDeleteClick,
    } = this.props

    return (
      <div className="DeleteDialog">
        <div className="deleteText is-size-7">
          En confirmant l'annulation de{' '}
          {isStockOnly ? 'ce stock' : 'cette date'}, vous supprimerez aussi
          toutes les réservations associées. {!isStockOnly && <br />}
          Êtes-vous sûrs de vouloir continuer&nbsp;?
        </div>

        <div className="deleteActions">
          <button className="button is-primary" onClick={onConfirmDeleteClick}>
            Oui
          </button>

          <button className="button is-primary" onClick={onCancelDeleteClick}>
            Non
          </button>
        </div>
      </div>
    )
  }
}

export default Delete
