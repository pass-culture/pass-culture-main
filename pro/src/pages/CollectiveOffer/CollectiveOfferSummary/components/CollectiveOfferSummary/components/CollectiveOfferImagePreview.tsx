import cn from 'classnames'
import { useId } from 'react'

import type {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import strokeOfferIcon from '@/icons/stroke-offer.svg'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './CollectiveOfferImagePreview.module.scss'

interface CollectiveOfferImagePreviewProps {
  offer:
    | GetCollectiveOfferTemplateResponseModel
    | GetCollectiveOfferResponseModel
}

export const CollectiveOfferImagePreview = ({
  offer,
}: CollectiveOfferImagePreviewProps): JSX.Element => {
  const imageCreditId = useId()
  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )

  return (
    <SummarySubSection
      title="Image de l'offre"
      shouldShowDivider={!isNewCollectivePriceEnabled}
    >
      {offer.imageUrl ? (
        <figure className={styles['image-credit']}>
          <img
            alt={offer.name}
            src={offer.imageUrl}
            className={styles['image-preview']}
            aria-describedby={offer.imageCredit ? imageCreditId : undefined}
          />
          {offer.imageCredit ? (
            <figcaption id={imageCreditId}>
              <p className={styles['image-credit-text']}>
                Crédit image : {offer.imageCredit}
              </p>
            </figcaption>
          ) : null}
        </figure>
      ) : (
        <div className={cn(styles['default-preview'], styles['image-preview'])}>
          <SvgIcon
            alt={offer.name}
            src={strokeOfferIcon}
            className={styles['default-preview-icon']}
          />
        </div>
      )}
    </SummarySubSection>
  )
}
