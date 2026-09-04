import { getOfferEnhancementActionsVisibility } from 'commons/core/Offers/utils/getOfferEnhancementActionsVisibility'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { getDepartmentCode } from '@/commons/utils/getDepartmentCode'
import { isSelectedPartnerOrOffererClosed } from '@/commons/utils/isSelectedPartnerOrOffererClosed'
import { DisplayOfferInAppLink } from '@/components/DisplayOfferInAppLink/DisplayOfferInAppLink'
import { OfferHeadlineCard } from '@/components/IndividualOfferLayout/components/OfferHeadlineCard/OfferHeadlineCard'
import { OfferHighlightCard } from '@/components/IndividualOfferLayout/components/OfferHighlightCard/OfferHighlightCard'
import { OfferRecommendationCard } from '@/components/IndividualOfferLayout/components/OfferRecommendationCard/OfferRecommendationCard'
import { OfferAppPreview } from '@/components/OfferAppPreview/OfferAppPreview'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'
import { SummaryAside } from '@/ui-kit/SummaryLayout/SummaryAside'
import { SummaryContent } from '@/ui-kit/SummaryLayout/SummaryContent'
import { SummaryLayout } from '@/ui-kit/SummaryLayout/SummaryLayout'

import { OfferExposureCards } from './components/OfferExposureCards/OfferExposureCards'
import { OfferExposureTimeline } from './components/OfferExposureTimeline/OfferExposureTimeline'
import styles from './IndividualOfferExposureScreen.module.scss'

export type IndividualOfferExposureScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}
export const IndividualOfferExposureScreen = ({
  offer,
}: Readonly<IndividualOfferExposureScreenProps>) => {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)

  const isClosed = isSelectedPartnerOrOffererClosed(selectedPartnerVenue)
  const {
    shouldDisplayRecommendationAction,
    shouldDisplayHighlightAction,
    shouldDisplayHeadlineAction,
  } = getOfferEnhancementActionsVisibility(offer)

  return (
    <SummaryLayout className={styles['individual-offer-exposure-screen']}>
      <SummaryContent>
        <OfferExposureCards offer={offer} />
        {(shouldDisplayRecommendationAction || shouldDisplayHeadlineAction) && (
          <h2 className={styles['title']}>Actions de mise en avant</h2>
        )}
        <div className={styles['cards-container']}>
          {shouldDisplayRecommendationAction && (
            <OfferRecommendationCard isReadOnly={isClosed} offerId={offer.id} />
          )}
          {shouldDisplayHighlightAction && (
            <OfferHighlightCard
              offerId={offer.id}
              highlightRequests={offer.highlightRequests}
              isReadOnly={isClosed}
            />
          )}
          {shouldDisplayHeadlineAction && (
            <OfferHeadlineCard
              isReadOnly={isClosed}
              offerId={offer.id}
              hasThumb={!!offer.thumbUrl}
            />
          )}
        </div>
        <OfferExposureTimeline
          offerId={offer.id}
          creationDate={offer.dateCreated}
          departmentCode={getDepartmentCode(offer, selectedPartnerVenue)}
        />
      </SummaryContent>

      <SummaryAside>
        <div className={styles['button-see-in-app']}>
          <DisplayOfferInAppLink
            id={offer.id}
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            label="Visualiser dans l’app"
            iconPosition={IconPositionEnum.LEFT}
            size={ButtonSize.SMALL}
            icon={fullLinkIcon}
            disabled={isClosed}
          />
        </div>
        <OfferAppPreview offer={offer} />
      </SummaryAside>
    </SummaryLayout>
  )
}
