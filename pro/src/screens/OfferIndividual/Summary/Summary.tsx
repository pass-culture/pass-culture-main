import React, { useState } from 'react'
import { useSelector } from 'react-redux'
import { useHistory, useLocation } from 'react-router-dom'

import useAnalytics from 'components/hooks/useAnalytics'
import useNotification from 'components/hooks/useNotification'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import { DisplayOfferInAppLink } from 'components/pages/Offers/Offer/DisplayOfferInAppLink'
import SynchronizedProviderInformation from 'components/pages/Offers/Offer/OfferDetails/OfferForm/SynchronisedProviderInfos'
import OfferStatusBanner from 'components/pages/Offers/Offer/OfferDetails/OfferStatusBanner'
import {
  Events,
  OFFER_FORM_NAVIGATION_MEDIUM,
  OFFER_FORM_NAVIGATION_OUT,
} from 'core/FirebaseEvents/constants'
import { computeOffersUrl } from 'core/Offers'
import { IOfferSubCategory } from 'core/Offers/types'
import { ReactComponent as PhoneInfo } from 'icons/info-phone.svg'
import { BannerSummary } from 'new_components/Banner'
import {
  IOfferAppPreviewProps,
  OfferAppPreview,
} from 'new_components/OfferAppPreview'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import { SummaryLayout } from 'new_components/SummaryLayout'
import * as pcapi from 'repository/pcapi/pcapi'
import { RootState } from 'store/reducers'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { getOfferConditionalFields } from 'utils/getOfferConditionalFields'

import { ActionBar } from '../ActionBar'

import { IOfferSectionProps, OfferSection } from './OfferSection'
import { IStockEventItemProps, StockEventSection } from './StockEventSection'
import { IStockThingSectionProps, StockThingSection } from './StockThingSection'
import styles from './Summary.module.scss'

export interface ISummaryProps {
  offerId: string
  formOfferV2?: boolean
  isCreation?: boolean
  providerName: string | null
  offerStatus: string
  offer: IOfferSectionProps
  stockThing?: IStockThingSectionProps
  stockEventList?: IStockEventItemProps[]
  subCategories: IOfferSubCategory[]
  preview: IOfferAppPreviewProps
}

const Summary = ({
  formOfferV2 = false,
  isCreation = false,
  providerName,
  offerStatus,
  offerId,
  offer,
  stockThing,
  stockEventList,
  subCategories,
  preview,
}: ISummaryProps): JSX.Element => {
  const [isDisabled, setIsDisabled] = useState(false)
  const location = useLocation()
  const notification = useNotification()
  const { logEvent } = useAnalytics()
  const handleOfferPublication = () => {
    setIsDisabled(true)
    const url = `/offre/${offerId}/individuel/creation/confirmation${location.search}`
    pcapi
      .publishOffer(offerId)
      .then(() => {
        setIsDisabled(false)
        logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
          from: OfferBreadcrumbStep.SUMMARY,
          to: OfferBreadcrumbStep.CONFIRMATION,
          used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
          isEdition: !isCreation,
        })
        history.push(url)
      })
      .catch(() => {
        notification.error("Une erreur s'est produite, veuillez réessayer")
        setIsDisabled(false)
      })
  }

  const history = useHistory()
  const handleNextStep = () => {
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OfferBreadcrumbStep.SUMMARY,
      to: OfferBreadcrumbStep.CONFIRMATION,
      used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
      isEdition: !isCreation,
    })
    history.push(`/offre/${offerId}/v3/creation/individuelle/confirmation`)
  }
  const handlePreviousStep = () => {
    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
      from: OfferBreadcrumbStep.SUMMARY,
      to: 'THIS ONE?',
      used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
      isEdition: !isCreation,
    })
    history.push(`/offre/${offerId}/v3/creation/individuelle/stocks`)
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

  const offersSearchFilters = useSelector(
    (state: RootState) => state.offers.searchFilters
  )
  const offersPageNumber = useSelector(
    (state: RootState) => state.offers.pageNumber
  )
  const backOfferUrl = computeOffersUrl(offersSearchFilters, offersPageNumber)

  const isDisabledOffer = isOfferDisabled(offerStatus)

  return (
    <>
      {(isCreation || isDisabledOffer || providerName !== null) && (
        <div className={styles['offer-preview-banners']}>
          {isCreation && <BannerSummary />}
          {isDisabledOffer && (
            <div className={styles['offer-preview-banner']}>
              <OfferStatusBanner status={offerStatus} />
            </div>
          )}
          {providerName !== null && (
            <div className={styles['offer-preview-banner']}>
              <SynchronizedProviderInformation providerName={providerName} />
            </div>
          )}
        </div>
      )}
      <SummaryLayout>
        <SummaryLayout.Content>
          <OfferSection
            conditionalFields={conditionalFields}
            offer={offer}
            isCreation={isCreation}
          />
          {stockThing && (
            <StockThingSection
              {...stockThing}
              isCreation={isCreation}
              offerId={offerId}
            />
          )}
          {stockEventList && (
            <StockEventSection
              stocks={stockEventList}
              isCreation={isCreation}
              offerId={offerId}
            />
          )}

          {formOfferV2 ? (
            isCreation ? (
              <div className={styles['offer-creation-preview-actions']}>
                <ButtonLink
                  variant={ButtonVariant.SECONDARY}
                  link={{
                    to: `/offre/${offerId}/individuel/creation/stocks`,
                    isExternal: false,
                  }}
                  onClick={() =>
                    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                      from: OfferBreadcrumbStep.SUMMARY,
                      to: OfferBreadcrumbStep.STOCKS,
                      used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
                      isEdition: !isCreation,
                    })
                  }
                >
                  Étape précédente
                </ButtonLink>
                <Button
                  variant={ButtonVariant.PRIMARY}
                  onClick={handleOfferPublication}
                  disabled={isDisabled}
                >
                  Publier l'offre
                </Button>
              </div>
            ) : (
              <div className={styles['offer-creation-preview-actions']}>
                <ButtonLink
                  variant={ButtonVariant.PRIMARY}
                  link={{ to: backOfferUrl, isExternal: false }}
                  onClick={() =>
                    logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                      from: OfferBreadcrumbStep.SUMMARY,
                      to: OFFER_FORM_NAVIGATION_OUT.OFFER,
                      used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
                      isEdition: !isCreation,
                    })
                  }
                >
                  Retour à la liste des offres
                </ButtonLink>
              </div>
            )
          ) : (
            <OfferFormLayout.ActionBar>
              <ActionBar
                onClickNext={handleNextStep}
                onClickPrevious={handlePreviousStep}
              />
            </OfferFormLayout.ActionBar>
          )}
        </SummaryLayout.Content>

        <SummaryLayout.Side>
          <div className={styles['offer-creation-preview-title']}>
            <PhoneInfo />
            <span>Aperçu dans l'app</span>
          </div>
          <OfferAppPreview {...preview} />
          {!isCreation && (
            <div className={styles['offer-preview-app-link']}>
              <DisplayOfferInAppLink nonHumanizedId={offer.nonHumanizedId} />
            </div>
          )}
        </SummaryLayout.Side>
      </SummaryLayout>
    </>
  )
}

export default Summary
