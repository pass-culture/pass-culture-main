import cn from 'classnames'

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
  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )

  return (
    <SummarySubSection
      title="Image de l'offre"
      shouldShowDivider={!isNewCollectivePriceEnabled}
    >
      {offer.imageUrl ? (
        <img
          alt={offer.name}
          src={offer.imageUrl}
          className={styles['image-preview']}
        />
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
