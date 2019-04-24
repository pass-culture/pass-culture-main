import React, { Component } from 'react'

class DeleteDialog extends Component {
  render() {
    const { isEvent, onCancelDeleteClick, onConfirmDeleteClick } = this.props

    return (
      <tr>
        <td colSpan="6" className="is-size-7">
          En confirmant l'annulation de {isEvent ? 'cette date' : 'ce stock'},
          vous supprimerez aussi toutes les réservations associées.{' '}
          {isEvent && <br />}
          Êtes-vous sûr de vouloir continuer&nbsp;?
        </td>

        <td>
          <button className="button is-primary" onClick={onConfirmDeleteClick}>
            Oui
          </button>
        </td>
        <td>
          <button className="button is-primary" onClick={onCancelDeleteClick}>
            Non
          </button>
        </td>
      </tr>
    )
  }
}

export default DeleteDialog
