import fullEditIcon from 'icons/full-edit.svg'

import {
  Banner,
  type BannerLink,
  BannerVariants,
} from '@/design-system/Banner/Banner'

import styles from '../BookableOfferTimeline.module.scss'

export const EndBanner = ({
  offerId,
  canEditDiscount,
}: {
  offerId: number
  canEditDiscount: boolean
}) => {
  const actions: BannerLink[] = canEditDiscount
    ? [
        {
          label: "Modifier à la baisse le prix ou le nombre d'élèves",
          href: `/offre/${offerId}/collectif/stocks/edition`,
          icon: fullEditIcon,
          type: 'link',
        },
      ]
    : []

  const description =
    'Nous espérons que votre évènement s’est bien déroulé. Si besoin, vous pouvez annuler la réservation ou modifier à la baisse le prix ou le nombre de participants jusqu’à 48 heures après la date de l’évènement.'

  return (
    <div className={styles['callout']}>
      <Banner
        title="Informations"
        variant={BannerVariants.DEFAULT}
        description={description}
        actions={actions}
      />
    </div>
  )
}
