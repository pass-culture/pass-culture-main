import { getOfferEnhancementActionsVisibility } from 'commons/core/Offers/utils/getOfferEnhancementActionsVisibility'
import { QRCodeSVG } from 'qrcode.react'
import { useNavigate } from 'react-router'

import type { GetIndividualOfferResponseModel } from '@/apiClient/v1'
import { OfferStatus } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { WEBAPP_URL } from '@/commons/utils/config'
import { isDateValid } from '@/commons/utils/date'
import { isSelectedPartnerOrOffererClosed } from '@/commons/utils/isSelectedPartnerOrOffererClosed'
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
  const isOfferExposureEnabled = useActiveFeature('WIP_OFFER_EXPOSURE')

  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const navigate = useNavigate()

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
    shouldDisplayRecommendationAction,
    shouldDisplayHighlightAction,
    shouldDisplayHeadlineAction,
  } = getOfferEnhancementActionsVisibility(offer)

  const isClosed = isSelectedPartnerOrOffererClosed(selectedPartnerVenue)
  const shouldDisplayCardsSection =
    shouldDisplayRecommendationAction ||
    shouldDisplayHighlightAction ||
    shouldDisplayHeadlineAction

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
            as="router-link"
            to={offerCreationUrl}
            variant={ButtonVariant.SECONDARY}
            label="Créer une nouvelle offre"
          />

          <Button
            as="router-link"
            to="/offres"
            label="Accéder à la liste des offres"
          />
        </div>
      </div>

      {shouldDisplayCardsSection && (
        <section className={styles['enhancement']}>
          <h2 className={styles['enhancement-title']}>
            Allez plus loin et optimisez votre offre :
          </h2>
          <div className={styles['enhancement-cards']}>
            {shouldDisplayRecommendationAction && (
              <OfferRecommendationCard
                isReadOnly={isClosed}
                offerId={offer.id}
                onSubmit={goToOfferPage}
                submitLabel="Enregistrer et accéder à l’offre"
              />
            )}
            {shouldDisplayHighlightAction && (
              <OfferHighlightCard
                isReadOnly={isClosed}
                offerId={offer.id}
                highlightRequests={offer.highlightRequests}
                onSubmit={goToOfferPage}
                submitLabel="Enregistrer et accéder à l’offre"
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
        </section>
      )}
    </div>
  )
}
