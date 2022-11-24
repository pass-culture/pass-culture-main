import cn from 'classnames'
import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
import { CollectiveOfferTemplate, CollectiveOffer } from 'core/OfferEducational'
import { ReactComponent as SVGOffers } from 'icons/ico-list-offers.svg'

import styles from './CollectiveOfferImagePreview.module.scss'

interface ICollectiveOfferImagePreviewProps {
  offer: CollectiveOfferTemplate | CollectiveOffer
}

const CollectiveOfferImagePreview = ({
  offer,
}: ICollectiveOfferImagePreviewProps): JSX.Element => {
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
          <SVGOffers title={offer.name} />
        </div>
      )}
    </SummaryLayout.SubSection>
  )
}

export default CollectiveOfferImagePreview
