import { Banner, BannerVariants } from '@/design-system/Banner/Banner'

import styles from './EanSearchCallout.module.scss'

type EanSearchCalloutProps = {
  isDraftOffer: boolean
}

export const EanSearchCallout = ({ isDraftOffer }: EanSearchCalloutProps) => {
  const calloutVariant = isDraftOffer
    ? BannerVariants.SUCCESS
    : BannerVariants.DEFAULT
  const calloutLabel = isDraftOffer
    ? 'Ces informations ont été récupérées depuis l’EAN.'
    : 'Ces informations proviennent de l’EAN et ne peuvent pas être modifiées.'
  const calloutTitle = isDraftOffer
    ? 'Synchronisation réussie.'
    : 'Informations verrouillées'

  return (
    <div className={styles['ean-search-callout']}>
      <Banner
        title={calloutTitle}
        variant={calloutVariant}
        description={calloutLabel}
      />
    </div>
  )
}
