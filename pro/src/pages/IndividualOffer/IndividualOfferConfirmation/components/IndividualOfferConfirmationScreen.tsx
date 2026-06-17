import { QRCodeSVG } from 'qrcode.react'
import { useNavigate } from 'react-router'

import type { GetIndividualOfferResponseModel } from '@/apiClient/v1/new'
import { OfferStatus } from '@/apiClient/v1/new'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { getOfferEnhancementCardsVisibility } from '@/commons/core/Offers/utils/getOfferEnhancementCardsVisibility'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { WEBAPP_URL } from '@/commons/utils/config'
import { isDateValid } from '@/commons/utils/date'
import { DisplayOfferInAppLink } from '@/components/DisplayOfferInAppLink/DisplayOfferInAppLink'
import { OfferHeadlineCard } from '@/components/IndividualOfferLayout/components/OfferHeadlineCard/OfferHeadlineCard'
import { OfferHighlightCard } from '@/components/IndividualOfferLayout/components/OfferHighlightCard/OfferHighlightCard'
import { OfferRecommendationCard } from '@/components/IndividualOfferLayout/components/OfferRecommendationCard/OfferRecommendationCard'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'
import fullWaitIcon from '@/icons/full-wait.svg'
import strokePartyIcon from '@/icons/stroke-party.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './IndividualOfferConfirmationScreen.module.scss'

interface IndividualOfferConfirmationScreenProps {
  offer: GetIndividualOfferResponseModel
}

export const IndividualOfferConfirmationScreen = ({
  offer,
}: IndividualOfferConfirmationScreenProps): JSX.Element => {
  const navigate = useNavigate()
  const isOfferExposureEnabled = useActiveFeature('WIP_OFFER_EXPOSURE')

  const isPublishedInTheFuture =
    isDateValid(offer.publicationDate) &&
    new Date() < new Date(offer.publicationDate)
  const isPendingOffer = offer.status === OfferStatus.PENDING

  const offerAppUrl = `${WEBAPP_URL}/offre/${offer.id}?utm_source=pro&utm_medium=qrcode&utm_gen=product&utm_campaign=proOfferPreview`

  const offerReadOnlyUrl = getIndividualOfferUrl({
    offerId: offer.id,
    step: isOfferExposureEnabled
      ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.EXPOSURE
      : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
    mode: OFFER_WIZARD_MODE.READ_ONLY,
    isOfferExposureEnabled,
  })

  const offerCreationUrl = getIndividualOfferUrl({
    step: INDIVIDUAL_OFFER_WIZARD_STEP_IDS.DESCRIPTION,
    mode: OFFER_WIZARD_MODE.CREATION,
    isOnboarding: false,
  })

  const goToOfferPage = () => {
    navigate(offerReadOnlyUrl)
  }

  const {
    shouldDisplayRecommendationCard,
    shouldDisplayHighlightCard,
    shouldDisplayHeadlineCard,
  } = getOfferEnhancementCardsVisibility(offer)

  const shouldDisplayCardsSection =
    shouldDisplayRecommendationCard ||
    shouldDisplayHighlightCard ||
    shouldDisplayHeadlineCard

  return (
    <div className={styles['container']}>
      {isPendingOffer ? (
        <h1 className={styles['title']}>
          Offre en cours de validation{' '}
          <span className={styles['title-icon']}>
            <SvgIcon src={fullWaitIcon} alt="" width="38" />
          </span>
        </h1>
      ) : (
        <h1 className={styles['title']}>
          Votre offre a été publiée avec succès{' '}
          <span className={styles['title-icon']}>
            <SvgIcon src={strokePartyIcon} alt="" width="38" />
          </span>
        </h1>
      )}
      {isPendingOffer && (
        <p className={styles['pending-details']}>
          Nous vérifions actuellement l’éligibilité de votre offre.{' '}
          <b>Cette vérification pourra prendre jusqu’à 72h.</b>
          <br />
          <b>Vous ne pouvez pas effectuer de modification pour l’instant.</b>
          <br />
          Vous recevrez un email de confirmation une fois votre offre validée.
        </p>
      )}
      <div className={styles['preview']}>
        {!isPublishedInTheFuture && !isPendingOffer && (
          <div className={styles['preview-qr-block']}>
            <QRCodeSVG
              value={offerAppUrl}
              size={108}
              className={styles['preview-qr']}
              aria-hidden
            />
            <div className={styles['preview-content']}>
              <p className={styles['preview-content-title']}>
                Visualisez votre offre sur l’application
              </p>
              <p className={styles['preview-content-subtitle']}>
                Scannez le QR code ou cliquez ci-dessous
              </p>
              <DisplayOfferInAppLink
                id={offer.id}
                icon={fullLinkIcon}
                variant={ButtonVariant.TERTIARY}
                color={ButtonColor.NEUTRAL}
                label="Visualiser sur le web"
              />
            </div>
          </div>
        )}
        <div className={styles['preview-actions']}>
          <Button
            as="a"
            to={offerCreationUrl}
            isExternal
            variant={ButtonVariant.SECONDARY}
            label="Créer une nouvelle offre"
          />

          <Button as="a" to="/offres" label="Accéder à la liste des offres" />
        </div>
      </div>

      {shouldDisplayCardsSection && (
        <section className={styles['enhancement']}>
          <h2 className={styles['enhancement-title']}>
            Allez plus loin et optimisez votre offre :
          </h2>
          <div className={styles['enhancement-cards']}>
            {shouldDisplayRecommendationCard && (
              <OfferRecommendationCard
                offerId={offer.id}
                onSubmit={goToOfferPage}
                submitLabel="Enregistrer et accéder à l’offre"
              />
            )}
            {shouldDisplayHighlightCard && (
              <OfferHighlightCard
                offerId={offer.id}
                highlightRequests={offer.highlightRequests}
                onSubmit={goToOfferPage}
                submitLabel="Enregistrer et accéder à l’offre"
              />
            )}
            {shouldDisplayHeadlineCard && (
              <OfferHeadlineCard
                offerId={offer.id}
                hasThumb={!!offer.thumbUrl}
              />
            )}
          </div>
        </section>
      )}
    </div>
  )
}
