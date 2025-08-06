import { Callout } from '@/ui-kit/Callout/Callout'
import { CalloutVariant } from '@/ui-kit/Callout/types'

import styles from '../BookableOfferTimeline.module.scss'

export const ArchivedBanner = () => {
  return (
    <Callout className={styles['callout']} variant={CalloutVariant.INFO}>
      {"Vous avez archivé cette offre. Elle n'est plus visible sur ADAGE."}
    </Callout>
  )
}
