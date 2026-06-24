import { Banner, BannerVariants } from '@/design-system/Banner/Banner'

import styles from './ProductBanner.module.scss'

export const ProductBanner = () => {
  return (
    <div className={styles['product-banner']}>
      <Banner
        title="Des informations proviennent d’un EAN et ne peuvent pas être modifiées depuis l’espace partenaire"
        variant={BannerVariants.WARNING}
      />
    </div>
  )
}
