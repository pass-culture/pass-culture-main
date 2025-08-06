import { OfferStatus } from '@/apiClient//v1'
import { CGU_URL } from '@/commons/utils/config'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

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
      <Callout className={styles['callout-offre-validation']}>
        Nous vérifions actuellement l’éligibilité de votre offre.
        <b>
          {' '}
          Cette vérification pourra prendre jusqu’à 72h. Vous ne pouvez pas
          effectuer de modification pour l’instant.{' '}
        </b>
        Vous recevrez un e-mail de confirmation une fois votre offre validée.
      </Callout>
    )
  }
  return <></>
}
