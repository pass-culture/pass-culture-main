import fullNextIcon from '@/icons/full-next.svg'
import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

import styles from '../BookableOfferTimeline.module.scss'

export const ReimbursedBanner = () => {
  return (
    <Callout
      className={styles['callout']}
      variant={CalloutVariant.INFO}
      links={[
        {
          label: 'Consulter les remboursements',
          href: '/remboursements',
          icon: {
            src: fullNextIcon,
            alt: 'Consulter les remboursements',
          },
        },
      ]}
    >
      Votre offre a été remboursée.
    </Callout>
  )
}
