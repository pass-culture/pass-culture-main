import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { Banner } from 'ui-kit'
import { CGU_URL } from 'utils/config'

interface IOfferStatusBanner {
  status: OfferStatus
}

const OfferStatusBanner = ({ status }: IOfferStatusBanner): JSX.Element => {
  if (status === OfferStatus.REJECTED) {
    return (
      <Banner
        links={[
          {
            href: CGU_URL,
            linkTitle: 'Consulter les Conditions Générales d’Utilisation',
          },
        ]}
      >
        Votre offre a été refusée car elle ne respecte pas les Conditions
        Générales d’Utilisation du pass. Un email contenant les conditions
        d’éligibilité d’une offre a été envoyé à l’adresse email attachée à
        votre compte.
      </Banner>
    )
  } else if (status == OfferStatus.PENDING) {
    return (
      <Banner type="notification-info">
        Votre offre est en cours de validation par l’équipe du pass Culture.
        <b>
          {' '}
          Cette vérification pourra prendre jusqu’à 72h. Vous ne pouvez pas
          effectuer de modification pour l’instant.{' '}
        </b>
        Une fois validée, vous recevrez un email de confirmation et votre offre
        sera automatiquement mise en ligne.
      </Banner>
    )
  }
  return <></>
}

export default OfferStatusBanner
