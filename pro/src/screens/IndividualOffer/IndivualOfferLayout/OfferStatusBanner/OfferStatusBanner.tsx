import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { Callout } from 'components/Callout/Callout'
import { CalloutVariant } from 'components/Callout/types'
import { CGU_URL } from 'utils/config'

import styles from './OfferStatusBanner.module.scss'
interface OfferStatusBannerProps {
  status: OfferStatus
}

export const OfferStatusBanner = ({
  status,
}: OfferStatusBannerProps): JSX.Element => {
  if (status === OfferStatus.REJECTED) {
    return (
      <Callout
        variant={CalloutVariant.ERROR}
        className={styles['callout-offre-refused']}
        links={[
          {
            href: CGU_URL,
            label: 'Consulter les Conditions Générales d’Utilisation',
            isExternal: true,
          },
        ]}
      >
        Votre offre a été refusée car elle ne respecte pas les Conditions
        Générales d’Utilisation du pass. Un email contenant les conditions
        d’éligibilité d’une offre a été envoyé à l’adresse email attachée à
        votre compte.
      </Callout>
    )
  } else if (status === OfferStatus.PENDING) {
    return (
      <Callout
        variant={CalloutVariant.INFO}
        className={styles['callout-offre-validation']}
      >
        Votre offre est en cours de validation par l’équipe du pass Culture.
        <b>
          {' '}
          Cette vérification pourra prendre jusqu’à 72h. Vous ne pouvez pas
          effectuer de modification pour l’instant.{' '}
        </b>
        Une fois validée, vous recevrez un email de confirmation et votre offre
        sera automatiquement mise en ligne.
      </Callout>
    )
  }
  return <></>
}
