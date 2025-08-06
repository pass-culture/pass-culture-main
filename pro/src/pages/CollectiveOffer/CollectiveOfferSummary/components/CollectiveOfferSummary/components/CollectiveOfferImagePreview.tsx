import cn from 'classnames'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
} from '@/apiClient/v1'
import { SummarySubSection } from '@/components/SummaryLayout/SummarySubSection'
import strokeOfferIcon from '@/icons/stroke-offer.svg'
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
  return (
    <SummarySubSection title="Image de l’offre">
      {offer.imageUrl ? (
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
    </SummarySubSection>
  )
}
