import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { BannerSummary } from 'components/Banner'
import RedirectDialog from 'components/Dialog/RedirectDialog'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferBreadcrumb/constants'
import { OfferAppPreview } from 'components/OfferAppPreview'
import { SummaryLayout } from 'components/SummaryLayout'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { Events, VenueEvents } from 'core/FirebaseEvents/constants'
import { getIndividualOfferAdapter } from 'core/Offers/adapters'
import { publishIndividualOffer } from 'core/Offers/adapters/publishIndividualOffer'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { getIndividualOfferUrl } from 'core/Offers/utils/getIndividualOfferUrl'
import { useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import fullWaitIcon from 'icons/full-wait.svg'
import strokePartyIcon from 'icons/stroke-party.svg'
import phoneStrokeIcon from 'icons/stroke-phone.svg'
import { DisplayOfferInAppLink } from 'screens/IndividualOffer/Summary/DisplayOfferInAppLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { getOfferConditionalFields } from 'utils/getOfferConditionalFields'

import { ActionBar } from '../ActionBar'

import { OfferSection } from './OfferSection'
import { PriceCategoriesSection } from './PriceCategoriesSection/PriceCategoriesSection'
import { StockSection } from './StockSection'
import styles from './Summary.module.scss'

const Summary = () => {
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
  } = useIndividualOfferContext()
  const { logEvent } = useAnalytics()

  if (offer === null) {
    return null
  }
  const canBeDuo = subCategories.find(
    subCategory => subCategory.id === offer.subcategoryId
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
    const response = await publishIndividualOffer({
      offerId: offer.id,
    })
    if (response.isOk) {
      const response = await getIndividualOfferAdapter(offer.id)
      if (response.isOk) {
        setOffer && setOffer(response.payload)
      }
      if (showVenuePopin[venueId || '']) {
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
  const offerSubCategory = subCategories.find(s => s.id === offer.subcategoryId)

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
      {(mode === OFFER_WIZARD_MODE.CREATION ||
        mode === OFFER_WIZARD_MODE.DRAFT) && (
        <div className={styles['offer-preview-banners']}>
          <BannerSummary mode={mode} />
        </div>
      )}

      <SummaryLayout>
        <SummaryLayout.Content>
          <OfferSection conditionalFields={conditionalFields} offer={offer} />

          {(mode === OFFER_WIZARD_MODE.CREATION ||
            mode === OFFER_WIZARD_MODE.DRAFT) &&
            offer.isEvent && (
              <PriceCategoriesSection offer={offer} canBeDuo={canBeDuo} />
            )}

          {(mode === OFFER_WIZARD_MODE.CREATION ||
            mode === OFFER_WIZARD_MODE.DRAFT) && (
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
              />
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
          redirectText="Renseigner des coordonnées bancaires"
          redirectLink={{
            to: `/structures/${offerOfferer?.id}/lieux/${venueId}?modification#remboursement`,
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
          <p>Vous pouvez dès à présent renseigner des coordonnées bancaires.</p>
          <p>
            Vos remboursements seront rétroactifs une fois vos coordonnées
            bancaires validées.
          </p>
        </RedirectDialog>
      )}
    </>
  )
}

export default Summary
