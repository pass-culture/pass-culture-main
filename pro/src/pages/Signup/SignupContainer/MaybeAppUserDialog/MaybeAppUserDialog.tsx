import './MaybeAppUserDialog.scss'

import React from 'react'

import RedirectDialog from 'components/Dialog/RedirectDialog'
import FraudIcon from 'icons/fraud.svg'

const MaybeAppUserDialog = ({ onCancel }: { onCancel: () => void }) => {
  return (
    <RedirectDialog
      icon={FraudIcon}
      redirectText="S’inscrire sur l’application pass Culture"
      redirectLink={{
        to: 'https://passculture.app/',
        isExternal: true,
      }}
      cancelText="Continuer vers le pass Culture Pro"
      title="Il semblerait que tu ne sois pas"
      secondTitle={` un professionnel de la culture`}
      onCancel={onCancel}
    >
      <p>
        Tu essayes de t’inscrire sur l’espace pass Culture Pro dédié aux
        professionnels de la culture. Pour créer ton compte, rends-toi sur
        l’application pass Culture.
      </p>
    </RedirectDialog>
  )
}

export default MaybeAppUserDialog
