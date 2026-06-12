import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1/new'
import { getOfferEnhancementCardsVisibility } from '@/commons/core/Offers/utils/getOfferEnhancementCardsVisibility'
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

import styles from './IndividualOfferExposureScreen.module.scss'

export type IndividualOfferExposureScreenProps = {
  offer: GetIndividualOfferWithAddressResponseModel
}
export const IndividualOfferExposureScreen = ({
  offer,
}: Readonly<IndividualOfferExposureScreenProps>) => {
  const {
    shouldDisplayRecommendationCard,
    shouldDisplayHighlightCard,
    shouldDisplayHeadlineCard,
  } = getOfferEnhancementCardsVisibility(offer)

  return (
    <SummaryLayout>
      <SummaryContent>
        <h2 className={styles['title']}>Actions de mise en avant</h2>
        <div className={styles['cards-container']}>
          {shouldDisplayRecommendationCard && (
            <OfferRecommendationCard offerId={offer.id} />
          )}
          {shouldDisplayHighlightCard && (
            <OfferHighlightCard
              offerId={offer.id}
              highlightRequests={offer.highlightRequests}
            />
          )}
          {shouldDisplayHeadlineCard && (
            <OfferHeadlineCard offerId={offer.id} hasThumb={!!offer.thumbUrl} />
          )}
        </div>
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
          />
        </div>
        <OfferAppPreview offer={offer} />
      </SummaryAside>
    </SummaryLayout>
  )
}
