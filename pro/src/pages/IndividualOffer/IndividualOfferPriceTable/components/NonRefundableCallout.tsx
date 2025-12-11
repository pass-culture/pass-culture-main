import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullLinkIcon from '@/icons/full-link.svg'

import styles from './IndividualOfferPriceTableScreen.module.scss'

export const NonRefundableCallout = () => (
  <div className={styles['callout']}>
    <Banner
      actions={[
        {
          href: 'https://aide.passculture.app/hc/fr/articles/6043184068252',
          isExternal: true,
          label: 'Quelles sont les offres éligibles au remboursement ?',
          icon: fullLinkIcon,
          iconAlt: 'Nouvelle fenêtre',
          type: 'link',
        },
      ]}
      title=""
      variant={BannerVariants.WARNING}
      description="Cette offre ne sera pas remboursée."
    />
  </div>
)
