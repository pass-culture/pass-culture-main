import PropTypes from 'prop-types'
import React, { useCallback } from 'react'

import * as pcapi from 'repository/pcapi/pcapi'

export const DeleteStockConfirmation = ({ refreshOffer, setIsDeleting, stockId }) => {
  const confirmStockDeletion = useCallback(() => {
    pcapi.deleteStock(stockId).then(() => refreshOffer())
  }, [refreshOffer, stockId])

  const abortStockDeletion = useCallback(() => setIsDeleting(false), [setIsDeleting])

  return (
    <tr>
      <td
        className="delete-confirmation"
        colSpan="7"
      >
        {
          'En confirmant l’annulation de cette date, vous supprimerez aussi toutes les réservations associées.'
        }
        <br />
        {'L’ensemble des utilisateurs seront automatiquement avertis par mail.'}
        <br />
        {'Êtes-vous sûr de vouloir continuer ?'}
      </td>
      <td>
        <button
          className="secondary-button"
          onClick={confirmStockDeletion}
          type="button"
        >
          {'Oui'}
        </button>
      </td>
      <td>
        <button
          className="secondary-button"
          onClick={abortStockDeletion}
          type="button"
        >
          {'Non'}
        </button>
      </td>
    </tr>
  )
}

DeleteStockConfirmation.propTypes = {
  refreshOffer: PropTypes.func.isRequired,
  setIsDeleting: PropTypes.func.isRequired,
  stockId: PropTypes.string.isRequired,
}
