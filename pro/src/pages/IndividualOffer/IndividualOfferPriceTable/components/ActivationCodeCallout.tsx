import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

import styles from './IndividualOfferPriceTableScreen.module.scss'

export const ActivationCodeCallout = () => (
  <Callout
    className={styles['callout']}
    links={[
      {
        href: 'https://aide.passculture.app/hc/fr/articles/4411991970705--Acteurs-culturels-Comment-cr%C3%A9er-une-offre-num%C3%A9rique-avec-des-codes-d-activation',
        isExternal: true,
        label: 'Comment gérer les codes d’activation ?',
      },
    ]}
    variant={CalloutVariant.INFO}
  >
    Vous pouvez, sur cette page, ajouter des codes d’activation si vous le
    souhaitez.
  </Callout>
)
