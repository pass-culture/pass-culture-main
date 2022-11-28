import React, { useState } from 'react'
import { useHistory } from 'react-router-dom'

import { api } from 'apiClient/api'
import { BannerSummary } from 'components/Banner'
import {
  IOfferAppPreviewProps,
  OfferAppPreview,
} from 'components/OfferAppPreview'
import { OfferBreadcrumbStep } from 'components/OfferBreadcrumb'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import { SummaryLayout } from 'components/SummaryLayout'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { isOfferDisabled, OFFER_WIZARD_MODE } from 'core/Offers'
import { IOfferSubCategory } from 'core/Offers/types'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { useOfferWizardMode } from 'hooks'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useNotification from 'hooks/useNotification'
import { ReactComponent as PhoneInfo } from 'icons/info-phone.svg'
import { DisplayOfferInAppLink } from 'pages/Offers/Offer/DisplayOfferInAppLink'
import OfferStatusBanner from 'pages/Offers/Offer/OfferDetails/OfferStatusBanner'
import { ButtonVariant } from 'ui-kit/Button/types'
import { getOfferConditionalFields } from 'utils/getOfferConditionalFields'

import { ActionBar } from '../ActionBar'
import { SynchronizedProviderInformation } from '../SynchronisedProviderInfos'

import { ActionsFormV2 } from './ActionsFormV2'
import { IOfferSectionProps, OfferSection } from './OfferSection'
import { StockSection } from './StockSection'
import { IStockEventItemProps } from './StockSection/StockEventSection'
import { IStockThingSectionProps } from './StockSection/StockThingSection'
import styles from './Summary.module.scss'

export interface ISummaryProps {
  offerId: string
  formOfferV2?: boolean
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
    formOfferV2 = false,
    providerName,
    offerId,
    offer,
    stockThing,
    stockEventList,
    subCategories,
    preview,
  }: ISummaryProps
): JSX.Element => {
  const [isDisabled, setIsDisabled] = useState(false)
  const notification = useNotification()
  const mode = useOfferWizardMode()
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')

  const { logEvent } = useAnalytics()
  const publishOffer = () => {
    // edition mode offers are already publish
    /* istanbul ignore next: DEBT, TO FIX */
    if (mode === OFFER_WIZARD_MODE.EDITION) {
      return
    }
    setIsDisabled(true)
    api
      // @ts-expect-error: type string is not assignable to type number
      .patchPublishOffer({ id: offerId })
      .then(() => {
        setIsDisabled(false)
        logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
          from: OfferBreadcrumbStep.SUMMARY,
          to: OfferBreadcrumbStep.CONFIRMATION,
          used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
          isEdition: false,
          isDraft: true,
          offerId: offerId,
        })
        history.push(
          getOfferIndividualUrl({
            offerId,
            step: OFFER_WIZARD_STEP_IDS.CONFIRMATION,
            mode,
            isV2: !isOfferFormV3,
          })
        )
      })
      .catch(
        /* istanbul ignore next: DEBT, TO FIX */
        () => {
          notification.error("Une erreur s'est produite, veuillez réessayer")
          setIsDisabled(false)
        }
      )
  }

  const history = useHistory()

  /* istanbul ignore next: DEBT, TO FIX */
  const handlePreviousStep = () => {
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OfferBreadcrumbStep.SUMMARY,
      to: OfferBreadcrumbStep.STOCKS,
      used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
      isEdition: mode !== OFFER_WIZARD_MODE.CREATION,
      isDraft: mode !== OFFER_WIZARD_MODE.EDITION,
      offerId: offerId,
    })

    history.push(
      getOfferIndividualUrl({
        offerId,
        step: OFFER_WIZARD_STEP_IDS.STOCKS,
        mode,
        isV2: !isOfferFormV3,
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

  const isDisabledOffer = isOfferDisabled(offer.status)

  return (
    <>
      {(mode !== OFFER_WIZARD_MODE.EDITION ||
        isDisabledOffer ||
        providerName !== null) && (
        <div className={styles['offer-preview-banners']}>
          {mode !== OFFER_WIZARD_MODE.EDITION && <BannerSummary mode={mode} />}
          {
            /* istanbul ignore next: DEBT, TO FIX */
            isDisabledOffer && (
              <div className={styles['offer-preview-banner']}>
                <OfferStatusBanner status={offer.status} />
              </div>
            )
          }
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
          {formOfferV2 ? (
            <ActionsFormV2
              offerId={offerId}
              className={styles['offer-creation-preview-actions']}
              publishOffer={publishOffer}
              disablePublish={isDisabled}
            />
          ) : (
            <ActionBar
              onClickNext={publishOffer}
              onClickPrevious={handlePreviousStep}
              step={OFFER_WIZARD_STEP_IDS.SUMMARY}
              isDisabled={isDisabled}
              offerId={offerId}
            />
          )}
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
                        from: OfferBreadcrumbStep.SUMMARY,
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
    </>
  )
}

export default Summary
