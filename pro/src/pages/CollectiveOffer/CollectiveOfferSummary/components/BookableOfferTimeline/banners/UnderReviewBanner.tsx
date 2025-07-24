import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'

import styles from '../BookableOfferTimeline.module.scss'

export const UnderReviewBanner = () => {
  return (
    <Callout className={styles['callout']} variant={CalloutVariant.INFO}>
      {
        "Votre offre est en cours d'instruction par notre équipe chargée du contrôle de conformité. Ce contrôle peut prendre jusqu'à 72 heures. Vous serez notifié par mail lors de sa validation ou de son refus."
      }
    </Callout>
  )
}
