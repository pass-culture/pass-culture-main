import cn from 'classnames'
import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
import { CollectiveOfferTemplate, CollectiveOffer } from 'core/OfferEducational'
import strokeOfferIcon from 'icons/stroke-offer.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './CollectiveOfferImagePreview.module.scss'

interface CollectiveOfferImagePreviewProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
}

const CollectiveOfferImagePreview = ({
  offer,
}: CollectiveOfferImagePreviewProps): JSX.Element => {
  return (
    <SummaryLayout.SubSection title="Image de l’offre">
      {offer?.imageUrl ? (
        <img
          alt={offer.name}
          src={offer.imageUrl}
          className={styles['image-preview']}
        />
      ) : (
        <div className={cn(styles['default-preview'], styles['image-preview'])}>
          <SvgIcon alt={offer.name} src={strokeOfferIcon} />
        </div>
      )}
    </SummaryLayout.SubSection>
  )
}

export default CollectiveOfferImagePreview
