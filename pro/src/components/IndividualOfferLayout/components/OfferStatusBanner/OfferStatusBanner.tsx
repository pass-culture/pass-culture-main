import { OfferStatus } from '@/apiClient/v1'
import { CGU_URL } from '@/commons/utils/config'
import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'

import styles from './OfferStatusBanner.module.scss'

interface OfferStatusBannerProps {
  status: OfferStatus
}

export const OfferStatusBanner = ({
  status,
}: OfferStatusBannerProps): JSX.Element => {
  if (status === OfferStatus.REJECTED) {
    return (
      <div className={styles['callout-offre-refused']}>
        <Banner
          title=""
          variant={BannerVariants.ERROR}
          actions={[
            {
              href: CGU_URL,
              label: 'Consulter les Conditions Générales d’Utilisation',
              isExternal: true,
              type: 'link',
              icon: fullLinkIcon,
              iconAlt: 'Nouvelle fenêtre',
            },
          ]}
          description="Votre offre a été refusée car elle ne respecte pas les Conditions
        Générales d’Utilisation du pass. Un email contenant les conditions
        d’éligibilité d’une offre a été envoyé à l’adresse email attachée à
        votre compte."
        />
      </div>
    )
  } else if (status === OfferStatus.PENDING) {
    return (
      <div className={styles['callout-offre-validation']}>
        <Banner
          title=""
          description={
            <>
              Nous vérifions actuellement l’éligibilité de votre offre.
              <b>
                {' '}
                Cette vérification pourra prendre jusqu’à 72h. Vous ne pouvez
                pas effectuer de modification pour l’instant.{' '}
              </b>
              Vous recevrez un e-mail de confirmation une fois votre offre
              validée.
            </>
          }
        />
      </div>
    )
  }
  return <></>
}
