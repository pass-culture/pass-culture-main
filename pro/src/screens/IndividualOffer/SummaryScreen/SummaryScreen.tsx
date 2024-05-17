import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { api } from 'apiClient/api'
import { getHumanReadableApiError } from 'apiClient/helpers'
import useAnalytics from 'app/App/analytics/firebase'
import { Callout } from 'components/Callout/Callout'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { OfferAppPreview } from 'components/OfferAppPreview/OfferAppPreview'
import { SummaryAside } from 'components/SummaryLayout/SummaryAside'
import { SummaryContent } from 'components/SummaryLayout/SummaryContent'
import { SummaryLayout } from 'components/SummaryLayout/SummaryLayout'
import { useIndividualOfferContext } from 'context/IndividualOfferContext/IndividualOfferContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import useNotification from 'hooks/useNotification'
import { useOfferWizardMode } from 'hooks/useOfferWizardMode'
import phoneStrokeIcon from 'icons/stroke-phone.svg'
import { RedirectToBankAccountDialog } from 'screens/Offers/RedirectToBankAccountDialog'
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
  const [isDisabled, setIsDisabled] = useState(false)
  const [displayRedirectDialog, setDisplayRedirectDialog] = useState(false)
  const notification = useNotification()
  const mode = useOfferWizardMode()
  const navigate = useNavigate()
  const { offerOfferer, offer, subCategories } = useIndividualOfferContext()
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

  const publishOffer = async () => {
    // edition mode offers are already publish
    /* istanbul ignore next: DEBT, TO FIX */
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      return
    }

    setIsDisabled(true)

    try {
      const offererResponse = await api.getOfferer(
        offer.venue.managingOfferer.id
      )
      const publishIndividualOfferResponse = await api.patchPublishOffer({
        id: offer.id,
      })

      const shouldDisplayRedirectDialog =
        publishIndividualOfferResponse.isNonFreeOffer &&
        !offererResponse.hasNonFreeOffer &&
        !offererResponse.hasValidBankAccount &&
        !offererResponse.hasPendingBankAccount

      if (shouldDisplayRedirectDialog) {
        setDisplayRedirectDialog(true)
      } else {
        navigate(offerConfirmationStepUrl)
      }
    } catch (error) {
      notification.error(getHumanReadableApiError(error))
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
          <Callout>
            <strong>Vous y êtes presque !</strong>
            <br />
            Vérifiez les informations ci-dessous avant de publier votre offre.
            <br />
            Si vous souhaitez la publier plus tard, vous pouvez retrouver votre
            brouillon dans la liste de vos offres.
          </Callout>
        </div>
      )}

      <SummaryLayout>
        <SummaryContent>
          <OfferSection conditionalFields={conditionalFields} offer={offer} />

          {mode === OFFER_WIZARD_MODE.CREATION && offer.isEvent && (
            <PriceCategoriesSection offer={offer} canBeDuo={canBeDuo} />
          )}

          {mode === OFFER_WIZARD_MODE.CREATION && (
            <StockSection offer={offer} canBeDuo={canBeDuo} />
          )}
        </SummaryContent>

        <SummaryAside>
          <div className={styles['offer-creation-preview-title']}>
            <SvgIcon
              src={phoneStrokeIcon}
              alt=""
              className={styles['icon-info-phone']}
            />
            <h2>Aperçu dans l’app</h2>
          </div>

          <OfferAppPreview offer={offer} />

          {mode === OFFER_WIZARD_MODE.READ_ONLY && (
            <div className={styles['offer-preview-app-link']}>
              <DisplayOfferInAppLink
                id={offer.id}
                variant={ButtonVariant.SECONDARY}
                onClick={() =>
                  logEvent(Events.CLICKED_OFFER_FORM_NAVIGATION, {
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
        </SummaryAside>
      </SummaryLayout>
      <ActionBar
        onClickNext={publishOffer}
        onClickPrevious={handlePreviousStep}
        step={OFFER_WIZARD_STEP_IDS.SUMMARY}
        isDisabled={isDisabled}
      />

      {displayRedirectDialog && offerOfferer?.id && offer.venue.id && (
        <RedirectToBankAccountDialog
          cancelRedirectUrl={offerConfirmationStepUrl}
          offerId={offerOfferer.id}
          venueId={offer.venue.id}
        />
      )}
    </>
  )
}

export default SummaryScreen
