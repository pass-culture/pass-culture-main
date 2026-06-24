import { Banner, BannerVariants } from '@/design-system/Banner/Banner'

import styles from './SynchronizedBanner.module.scss'

export const SynchronizedBanner = ({
  providerName,
}: {
  providerName?: string
}) => {
  return (
    <div className={styles['synchronized-banner']}>
      <Banner
        title={`Cette offre est synchronisée avec ${providerName ?? 'un fournisseur inconnu'}`}
        variant={BannerVariants.WARNING}
        description={
          'Certaines informations ne peuvent pas être modifiées depuis votre espace partenaire.'
        }
      />
    </div>
  )
}
