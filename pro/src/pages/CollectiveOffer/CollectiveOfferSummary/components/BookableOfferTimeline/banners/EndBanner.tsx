import fullEditIcon from 'icons/full-edit.svg'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'

import styles from '../BookableOfferTimeline.module.scss'

export const EndBanner = ({
  offerId,
  canEditDiscount,
}: {
  offerId: number
  canEditDiscount: boolean
}) => {
  return (
    <Callout
      className={styles['callout']}
      variant={CalloutVariant.INFO}
      links={[
        ...(canEditDiscount
          ? [
              {
                label: "Modifier à la baisse le prix ou le nombre d'élèves",
                href: `/offre/${offerId}/collectif/stocks/edition`,
                icon: {
                  src: fullEditIcon,
                  alt: "Editer l'offre",
                },
              },
            ]
          : []),
      ]}
    >
      {
        'Nous espérons que votre évènement s’est bien déroulé. Si besoin, vous pouvez annuler la réservation ou modifier à la baisse le prix ou le nombre de participants jusqu’à 48 heures après la date de l’évènement.'
      }
    </Callout>
  )
}
