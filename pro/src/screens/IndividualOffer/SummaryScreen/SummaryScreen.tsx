import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import RedirectDialog from 'components/Dialog/RedirectDialog'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { OfferAppPreview } from 'components/OfferAppPreview'
import { SummaryLayout } from 'components/SummaryLayout'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
  VenueEvents,
} from 'core/FirebaseEvents/constants'
import { serializeOfferApi } from 'core/Offers/adapters/getIndividualOfferAdapter/serializers'
import { publishIndividualOffer } from 'core/Offers/adapters/publishIndividualOffer'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import fullWaitIcon from 'icons/full-wait.svg'
import strokePartyIcon from 'icons/stroke-party.svg'
import phoneStrokeIcon from 'icons/stroke-phone.svg'
import Banner from 'ui-kit/Banners/Banner/Banner'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { getOfferConditionalFields } from 'utils/getOfferConditionalFields'

import ActionBar from '../ActionBar/ActionBar'

import { DisplayOfferInAppLink } from './DisplayOfferInAppLink/DisplayOfferInAppLink'
import OfferSection from './OfferSection/OfferSection'
import { PriceCategoriesSection } from './PriceCategoriesSection/PriceCategoriesSection'
import StockSection from './StockSection/StockSection'
import styles from './SummaryScreen.module.scss'

const SummaryScreen = () => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const [isDisabled, setIsDisabled] = useState(false)
  const [displayRedirectDialog, setDisplayRedirectDialog] = useState(false)
  const notification = useNotification()
  const mode = useOfferWizardMode()
  const navigate = useNavigate()
  const {
    setOffer,
    venueId,
    offerOfferer,
    showVenuePopin,
    offer,
    subCategories,
    venueList,
  } = useIndividualOfferContext()
  const { logEvent } = useAnalytics()

  if (offer === null) {
    return null
  }
  const canBeDuo = subCategories.find(
    (subCategory) => subCategory.id === offer.subcategoryId
  )?.canBeDuo

  const offerConfirmationStepUrl = getIndividualOfferUrl({
    offerId: offer.id,
    step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
    mode,
  })

  const checkFirstNonFreeOfferPopin = async (isNonFreeOffer: boolean) => {
    if (isNonFreeOffer) {
      navigate(offerConfirmationStepUrl)
    }

    const offererResponse = await api.getOfferer(offer.offererId)
    if (
      !offererResponse.hasPendingBankAccount &&
      !offererResponse.hasValidBankAccount
    ) {
      setDisplayRedirectDialog(true)
    } else {
      navigate(offerConfirmationStepUrl)
    }
  }

  const publishOffer = async () => {
    // edition mode offers are already publish
    /* istanbul ignore next: DEBT, TO FIX */
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      return
    }

    setIsDisabled(true)
    const venueHasCreatedNonFreeOffer = isNewBankDetailsJourneyEnabled
      ? venueList.some((venue) => {
          return venue.hasNonFreeOffers
        })
      : undefined

    const publishIndividualOfferResponse = await publishIndividualOffer({
      offerId: offer.id,
    })
    if (publishIndividualOfferResponse.isOk) {
      setOffer?.(serializeOfferApi(publishIndividualOfferResponse.payload))

      if (isNewBankDetailsJourneyEnabled && !venueHasCreatedNonFreeOffer) {
        await checkFirstNonFreeOfferPopin(
          publishIndividualOfferResponse.payload.isNonFreeOffer ?? false
        )
      } else if (
        !isNewBankDetailsJourneyEnabled &&
        showVenuePopin[venueId || '']
      ) {
        setDisplayRedirectDialog(true)
      } else {
        navigate(offerConfirmationStepUrl)
      }
    } else {
      notification.error("Une erreur s'est produite, veuillez réessayer")
    }
    setIsDisabled(false)
  }

  /* istanbul ignore next: DEBT, TO FIX */
  const handlePreviousStep = () => {
    navigate(
      getIndividualOfferUrl({
        offerId: offer.id,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        mode,
      })
    )
  }
  const offerSubCategory = subCategories.find(
    (s) => s.id === offer.subcategoryId
  )

  const offerConditionalFields = getOfferConditionalFields({
    offerSubCategory,
    isUserAdmin: false,
    receiveNotificationEmails: true,
    isVenueVirtual: offer.venue.isVirtual,
  })
  const subCategoryConditionalFields = offerSubCategory
    ? offerSubCategory.conditionalFields
    : []
  const conditionalFields = [
    ...subCategoryConditionalFields,
    ...offerConditionalFields,
  ]

  return (
    <>
      {mode === OFFER_WIZARD_MODE.CREATION && (
        <div className={styles['offer-preview-banners']}>
          <Banner type="notification-info">
            <strong>Vous y êtes presque !</strong>
            <br />
            Vérifiez les informations ci-dessous avant de publier votre offre.
            <br />
            Si vous souhaitez la publier plus tard, vous pouvez retrouver votre
            brouillon dans la liste de vos offres.
          </Banner>
        </div>
      )}

      <SummaryLayout>
        <SummaryLayout.Content>
          <OfferSection conditionalFields={conditionalFields} offer={offer} />

          {mode === OFFER_WIZARD_MODE.CREATION && offer.isEvent && (
            <PriceCategoriesSection offer={offer} canBeDuo={canBeDuo} />
          )}

          {mode === OFFER_WIZARD_MODE.CREATION && (
            <StockSection offer={offer} canBeDuo={canBeDuo} />
          )}

          <ActionBar
            onClickNext={publishOffer}
            onClickPrevious={handlePreviousStep}
            step={OFFER_WIZARD_STEP_IDS.SUMMARY}
            isDisabled={isDisabled}
          />
        </SummaryLayout.Content>

        <SummaryLayout.Side>
          <div className={styles['offer-creation-preview-title']}>
            <SvgIcon
              src={phoneStrokeIcon}
              alt=""
              className={styles['icon-info-phone']}
            />
            <span>Aperçu dans l'app</span>
          </div>

          <OfferAppPreview offer={offer} />

          {mode === OFFER_WIZARD_MODE.READ_ONLY && (
            <div className={styles['offer-preview-app-link']}>
              <DisplayOfferInAppLink
                id={offer.id}
                variant={ButtonVariant.SECONDARY}
                onClick={() =>
                  logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                    from: OFFER_WIZARD_STEP_IDS.SUMMARY,
                    to: OFFER_FORM_NAVIGATION_OUT.PREVIEW,
                    used: OFFER_FORM_NAVIGATION_MEDIUM.SUMMARY_PREVIEW,
                    isEdition: true,
                    isDraft: false,
                    offerId: offer.id,
                  })
                }
              >
                Visualiser dans l’app
              </DisplayOfferInAppLink>
            </div>
          )}
        </SummaryLayout.Side>
      </SummaryLayout>

      {displayRedirectDialog && (
        <RedirectDialog
          icon={strokePartyIcon}
          onCancel={() => {
            logEvent?.(
              Events.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL,
              {
                from: OFFER_WIZARD_STEP_IDS.SUMMARY,
              }
            )
            navigate(offerConfirmationStepUrl)
          }}
          title="Félicitations, vous avez créé votre offre !"
          redirectText={
            isNewBankDetailsJourneyEnabled
              ? 'Renseigner un compte bancaire'
              : 'Renseigner des coordonnées bancaires'
          }
          redirectLink={{
            to: isNewBankDetailsJourneyEnabled
              ? `remboursements/informations-bancaires?structure=${offerOfferer?.id}`
              : `/structures/${offerOfferer?.id}/lieux/${venueId}?modification#remboursement`,
            isExternal: false,
          }}
          onRedirect={() =>
            logEvent?.(VenueEvents.CLICKED_VENUE_ADD_RIB_BUTTON, {
              venue_id: venueId,
              from: OFFER_WIZARD_STEP_IDS.SUMMARY,
            })
          }
          cancelText="Plus tard"
          cancelIcon={fullWaitIcon}
          withRedirectLinkIcon={false}
        >
          <p>
            Vous pouvez dès à présent renseigner{' '}
            {isNewBankDetailsJourneyEnabled
              ? 'un compte bancaire'
              : 'des coordonnées bancaires'}
            .
          </p>
          <p>
            Vos remboursements seront rétroactifs une fois{' '}
            {isNewBankDetailsJourneyEnabled
              ? 'votre compte bancaire validé'
              : 'vos coordonnées bancaires validées'}
            .
          </p>
        </RedirectDialog>
      )}
    </>
  )
}

export default SummaryScreen
