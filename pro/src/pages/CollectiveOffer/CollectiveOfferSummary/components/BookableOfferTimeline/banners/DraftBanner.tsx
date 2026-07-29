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
            type: 'link',
          },
        ]}
        description="Finalisez et envoyez votre brouillon à un établissement quand vous le souhaitez."
        title="Brouillon en cours"
      />
    </div>
  )
}
