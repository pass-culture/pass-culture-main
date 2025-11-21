import { Banner } from '@/design-system/Banner/Banner'
import fullEditIcon from '@/icons/full-edit.svg'

import styles from '../BookableOfferTimeline.module.scss'

export const DraftBanner = ({ offerId }: { offerId: number }) => {
  return (
    <div className={styles['callout']}>
      <Banner
        actions={[
          {
            icon: fullEditIcon,
            iconAlt: 'Modifier',
            href: `/offre/collectif/${offerId}/creation`,
            label: 'Reprendre mon brouillon',
            type: 'button',
          },
        ]}
        description="Vous avez commencé à rédiger un brouillon. Vous pouvez le reprendre à tout moment afin de finaliser sa rédaction et l'envoyer à un établissement."
        title=""
      />
    </div>
  )
}
