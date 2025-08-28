import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

import styles from './IndividualOfferPriceTableScreen.module.scss'

export const NonRefundableCallout = () => (
  <Callout
    className={styles['callout']}
    links={[
      {
        href: 'https://aide.passculture.app/hc/fr/articles/6043184068252',
        isExternal: true,
        label: 'Quelles sont les offres éligibles au remboursement ?',
        target: '_blank',
      },
    ]}
    variant={CalloutVariant.WARNING}
  >
    Cette offre ne sera pas remboursée.
  </Callout>
)
