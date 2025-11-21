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
    ? 'Les informations suivantes ont été synchronisées à partir de l’EAN renseigné.'
    : 'Les informations de cette page ne sont pas modifiables car elles sont liées à l’EAN renseigné.'

  return (
    <div className={styles['ean-search-callout']}>
      <Banner title="" variant={calloutVariant} description={calloutLabel} />
    </div>
  )
}
