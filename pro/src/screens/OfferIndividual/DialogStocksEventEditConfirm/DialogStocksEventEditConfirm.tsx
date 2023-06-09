import React from 'react'

import ConfirmDialog from 'components/Dialog/ConfirmDialog'

interface IDialogStocksEventEditConfirmProps {
  onConfirm: () => void
  onCancel: () => void
}

const DialogStocksEventEditConfirm = ({
  onConfirm,
  onCancel,
}: IDialogStocksEventEditConfirmProps) => {
  return (
    <ConfirmDialog
      onCancel={onCancel}
      onConfirm={onConfirm}
      title="Des réservations sont en cours pour cette offre"
      confirmText="Confirmer les modifications"
      cancelText="Annuler"
    >
      <p>
        Si vous avez changé la date ou l'heure de l'évènement, les bénéficiaires
        ayant déjà réservé en seront automatiquement informés par email.
      </p>
      <p>
        Ils disposeront alors à nouveau de 48h pour annuler leur réservation.
      </p>
      <br />
      <p>
        Si vous avez changé le tarif de cette offre, celui-ci ne s'appliquera
        que pour les prochaines réservations.
      </p>
    </ConfirmDialog>
  )
}

export default DialogStocksEventEditConfirm
