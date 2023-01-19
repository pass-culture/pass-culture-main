import React, { useState } from 'react'

import { BannerSummary } from 'components/Banner'
import RedirectDialog from 'components/Dialog/RedirectDialog'
import {
  IOfferAppPreviewProps,
  OfferAppPreview,
} from 'components/OfferAppPreview'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { SummaryLayout } from 'components/SummaryLayout'
import { useOfferIndividualContext } from 'context/OfferIndividualContext'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
  VenueEvents,
} from 'core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from 'core/Offers'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import { publishIndividualOffer } from 'core/Offers/adapters/publishIndividualOffer'
import { IOfferSubCategory } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useNavigate, useOfferWizardMode } from 'hooks'
import useAnalytics from 'hooks/useAnalytics'
import useNewOfferCreationJourney from 'hooks/useNewOfferCreationJourney'
import useNotification from 'hooks/useNotification'
import { IcoParty } from 'icons'
import { ReactComponent as PhoneInfo } from 'icons/info-phone.svg'
import { DisplayOfferInAppLink } from 'screens/OfferIndividual/Summary/DisplayOfferInAppLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { getOfferConditionalFields } from 'utils/getOfferConditionalFields'

import { ActionBar } from '../ActionBar'
import { SynchronizedProviderInformation } from '../SynchronisedProviderInfos'

import { IOfferSectionProps, OfferSection } from './OfferSection'
import { StockSection } from './StockSection'
import { IStockEventItemProps } from './StockSection/StockEventSection'
import { IStockThingSectionProps } from './StockSection/StockThingSection'
import styles from './Summary.module.scss'

export interface ISummaryProps {
  offerId: string
  nonHumanizedOfferId: number
  providerName: string | null
  offer: IOfferSectionProps
  stockThing?: IStockThingSectionProps
  stockEventList?: IStockEventItemProps[]
  subCategories: IOfferSubCategory[]
  preview: IOfferAppPreviewProps
}

const Summary = (
  /* istanbul ignore next: DEBT, TO FIX */
  {
    providerName,
    offerId,
    nonHumanizedOfferId,
    offer,
    stockThing,
    stockEventList,
    subCategories,
    preview,
  }: ISummaryProps
): JSX.Element => {
  const [isDisabled, setIsDisabled] = useState(false)
  const [displayRedirectDialog, setDisplayRedirectDialog] = useState(false)
  const notification = useNotification()
  const mode = useOfferWizardMode()
  const navigate = useNavigate()
  const { setOffer, isFirstOffer, venueId, offerOfferer } =
    useOfferIndividualContext()
  const newOfferCreation = useNewOfferCreationJourney()

  const { logEvent } = useAnalytics()

  const offerConfirmationStepUrl = getOfferIndividualUrl({
    offerId,
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
      offerId: nonHumanizedOfferId,
    })
    if (response.isOk) {
      const response = await getOfferIndividualAdapter(offerId)
      if (response.isOk) {
        setOffer && setOffer(response.payload)
      }
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        from: OFFER_WIZARD_STEP_IDS.SUMMARY,
        to: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
        used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
        isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
        isDraft: true,
        offerId: offerId,
      })
      if (newOfferCreation && isFirstOffer) {
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
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OFFER_WIZARD_STEP_IDS.SUMMARY,
      to: OFFER_WIZARD_STEP_IDS.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
      offerId: offerId,
    })

    navigate(
      getOfferIndividualUrl({
        offerId,
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
    isVenueVirtual: offer.isVenueVirtual,
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
      {(mode !== OFFER_WIZARD_MODE.EDITION || providerName !== null) && (
        <div className={styles['offer-preview-banners']}>
          {mode !== OFFER_WIZARD_MODE.EDITION && <BannerSummary mode={mode} />}
          {providerName !== null && (
            <div className={styles['offer-preview-banner']}>
              <SynchronizedProviderInformation providerName={providerName} />
            </div>
          )}
        </div>
      )}
      <SummaryLayout>
        <SummaryLayout.Content>
          <OfferSection conditionalFields={conditionalFields} offer={offer} />
          <StockSection
            stockThing={stockThing}
            stockEventList={stockEventList}
            offerId={offerId}
            offerStatus={offer.status}
          />
          <ActionBar
            onClickNext={publishOffer}
            onClickPrevious={handlePreviousStep}
            step={OFFER_WIZARD_STEP_IDS.SUMMARY}
            isDisabled={isDisabled}
            offerId={offerId}
          />
        </SummaryLayout.Content>

        <SummaryLayout.Side>
          <div className={styles['offer-creation-preview-title']}>
            <PhoneInfo />
            <span>Aperçu dans l'app</span>
          </div>
          <OfferAppPreview {...preview} />
          {mode === OFFER_WIZARD_MODE.EDITION && (
            <div className={styles['offer-preview-app-link']}>
              <DisplayOfferInAppLink
                nonHumanizedId={offer.nonHumanizedId}
                tracking={{
                  isTracked: true,
                  trackingFunction:
                    /* istanbul ignore next: DEBT, TO FIX */
                    () =>
                      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                        from: OFFER_WIZARD_STEP_IDS.SUMMARY,
                        to: OFFER_FORM_NAVIGATION_OUT.PREVIEW,
                        used: OFFER_FORM_NAVIGATION_MEDIUM.SUMMARY_PREVIEW,
                        isEdition: true,
                        isDraft: false,
                        offerId: offerId,
                      }),
                }}
                variant={ButtonVariant.SECONDARY}
              />
            </div>
          )}
        </SummaryLayout.Side>
      </SummaryLayout>
      {newOfferCreation && displayRedirectDialog && (
        <RedirectDialog
          icon={IcoParty}
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
          withRedirectLinkIcon={false}
        >
          <p>Vous pouvez dès à présent renseigner des coordonnées bancaires.</p>
          <p>
            Vos remboursements seront rétroactifs une fois vos coordonnées
            bancaires ajoutées.
          </p>
        </RedirectDialog>
      )}
    </>
  )
}

export default Summary
