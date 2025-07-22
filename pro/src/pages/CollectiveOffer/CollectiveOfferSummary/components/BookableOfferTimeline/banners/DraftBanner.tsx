import fullEditIcon from 'icons/full-edit.svg'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'

import styles from '../BookableOfferTimeline.module.scss'

export const DraftBanner = ({ offerId }: { offerId: number }) => {
  return (
    <Callout
      className={styles['callout']}
      variant={CalloutVariant.INFO}
      links={[
        {
          icon: { src: fullEditIcon, alt: 'Modifier' },
          href: `/offre/collectif/${offerId}/creation`,
          label: 'Reprendre mon brouillon',
        },
      ]}
    >
      {
        "Vous avez commencé à rédiger un brouillon. Vous pouvez le reprendre à tout moment afin de finaliser sa rédaction et l'envoyer à un établissement."
      }
    </Callout>
  )
}
