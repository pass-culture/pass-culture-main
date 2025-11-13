import { Banner, BannerVariants } from '@/design-system/Banner/Banner'
import fullNextIcon from '@/icons/full-next.svg'

import styles from '../BookableOfferTimeline.module.scss'

export const ReimbursedBanner = () => {
  return (
    <div className={styles['callout']}>
      <Banner
        title="Informations"
        variant={BannerVariants.DEFAULT}
        description="Votre offre a été remboursée."
        links={[
          {
            label: 'Consulter les remboursements',
            href: '/remboursements',
            icon: fullNextIcon,
            type: 'link',
          },
        ]}
      />
    </div>
  )
}
