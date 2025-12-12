import { Banner } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'

import styles from './IndividualOfferPriceTableScreen.module.scss'

export const ActivationCodeCallout = () => (
  <div className={styles['callout']}>
    <Banner
      actions={[
        {
          href: 'https://aide.passculture.app/hc/fr/articles/4411991970705--Acteurs-culturels-Comment-cr%C3%A9er-une-offre-num%C3%A9rique-avec-des-codes-d-activation',
          isExternal: true,
          label: 'Comment gérer les codes d’activation ?',
          icon: fullLinkIcon,
          iconAlt: 'Nouvelle fenêtre',
          type: 'link',
        },
      ]}
      title="Codes d'activation"
      description="Ajoutez des codes d'activation sur cette page si nécessaire."
    />
  </div>
)
