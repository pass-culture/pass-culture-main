import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { getOfferEnhancementCardsVisibility } from '@/commons/core/Offers/utils/getOfferEnhancementCardsVisibility'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { DisplayOfferInAppLink } from '@/components/DisplayOfferInAppLink/DisplayOfferInAppLink'
import { OfferHeadlineCard } from '@/components/IndividualOfferLayout/components/OfferHeadlineCard/OfferHeadlineCard'
import { OfferHighlightCard } from '@/components/IndividualOfferLayout/components/OfferHighlightCard/OfferHighlightCard'
import { OfferRecommendationCard } from '@/components/IndividualOfferLayout/components/OfferRecommendationCard/OfferRecommendationCard'
import { OfferAppPreview } from '@/components/OfferAppPreview/OfferAppPreview'
import { Button } from '@/design-system/Button/Button'
import {
  ButtonColor,
  ButtonSize,
  ButtonVariant,
  IconPositionEnum,
} from '@/design-system/Button/types'
import fullArrowRightIcon from '@/icons/full-arrow-right.svg'
import fullLinkIcon from '@/icons/full-link.svg'
import strokeEventIcon from '@/icons/stroke-events.svg'
import { Card } from '@/ui-kit/Card/Card'
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
        <h2 className={styles['title']}>Statistiques de votre offre</h2>
        <div className={styles['stats-container']}>
          <Card>
            <Card.Header
              titleTag="p"
              title={`${offer.bookingsCount ?? 0} ${pluralizeFr(offer.bookingsCount ?? 0, 'réservation', 'réservations')}`}
              subtitle="depuis la publication de votre offre"
              icon={strokeEventIcon}
            />
            <Card.Footer>
              <Button
                as="a"
                to={`${getIndividualOfferUrl({
                  offerId: offer.id,
                  step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.BOOKINGS,
                  mode: OFFER_WIZARD_MODE.EDITION,
                })}`}
                label="Voir les réservations"
                variant={ButtonVariant.TERTIARY}
                icon={fullArrowRightIcon}
                iconPosition={IconPositionEnum.LEFT}
                size={ButtonSize.SMALL}
              />
            </Card.Footer>
          </Card>
        </div>
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
