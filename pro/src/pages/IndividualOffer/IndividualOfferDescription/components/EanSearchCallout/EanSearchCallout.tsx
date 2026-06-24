import { Banner, BannerVariants } from '@/design-system/Banner/Banner'

import styles from './EanSearchCallout.module.scss'

export const EanSearchCallout = () => {
  return (
    <div className={styles['ean-search-callout']}>
      <Banner
        title={'Synchronisation réussie.'}
        variant={BannerVariants.SUCCESS}
        description={'Ces informations ont été récupérées depuis l’EAN.'}
      />
    </div>
  )
}
