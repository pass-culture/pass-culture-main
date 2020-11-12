import React from 'react'

const DeleteDialog = ({ isEvent, onCancelDeleteClick, onConfirmDeleteClick }) => (
  <tr>
    <td
      className="is-size-7"
      colSpan="6"
    >
      {'En confirmant l’annulation de '}
      {isEvent ? 'cette date' : 'ce stock'}
      {', '}
      {'vous supprimerez aussi toutes les réservations associées. '}
      <br />
      {"L'ensemble des utilisateurs seront automatiquement avertis par mail. "}
      <br />
      {'Êtes-vous sûr de vouloir continuer ?'}
    </td>

    <td>
      <button
        className="button is-primary"
        onClick={onConfirmDeleteClick}
        type="button"
      >
        {'Oui'}
      </button>
    </td>
    <td>
      <button
        className="button is-primary"
        onClick={onCancelDeleteClick}
        type="button"
      >
        {'Non'}
      </button>
    </td>
  </tr>
)

export default DeleteDialog
