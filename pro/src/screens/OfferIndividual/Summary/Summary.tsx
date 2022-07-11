import * as pcapi from 'repository/pcapi/pcapi'

import { Button, ButtonLink } from 'ui-kit'
import {
  IOfferAppPreviewProps,
  OfferAppPreview,
} from 'new_components/OfferAppPreview'
import { IOfferSectionProps, OfferSection } from './OfferSection'
import { IStockEventItemProps, StockEventSection } from './StockEventSection'
import { IStockThingSectionProps, StockThingSection } from './StockThingSection'
import React, { useState } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import { ActionBar } from '../ActionBar'
import { BannerSummary } from 'new_components/Banner'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DisplayOfferInAppLink } from 'components/pages/Offers/Offer/DisplayOfferInAppLink'
import { IOfferSubCategory } from 'core/Offers/types'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import { ReactComponent as PhoneInfo } from 'icons/info-phone.svg'
import { RootState } from 'store/reducers'
import { SummaryLayout } from 'new_components/SummaryLayout'
import { computeOffersUrl } from 'core/Offers'
import { getOfferConditionalFields } from 'utils/getOfferConditionalFields'
import styles from './Summary.module.scss'
import useNotification from 'components/hooks/useNotification'
import { useSelector } from 'react-redux'

export interface ISummaryProps {
  offerId: string
  formOfferV2?: boolean
  isCreation?: boolean
  offer: IOfferSectionProps
  stockThing?: IStockThingSectionProps
  stockEventList?: IStockEventItemProps[]
  subCategories: IOfferSubCategory[]
  preview: IOfferAppPreviewProps
}

const Summary = ({
  formOfferV2 = false,
  isCreation = false,
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
  const handleOfferPublication = () => {
    setIsDisabled(true)
    const url = `/offre/${offerId}/individuel/creation/confirmation${location.search}`
    pcapi
      .publishOffer(offerId)
      .then(() => {
        setIsDisabled(false)
        history.push(url)
      })
      .catch(() => {
        notification.error("Une erreur s'est produite, veuillez réessayer")
        setIsDisabled(false)
      })
  }

  const history = useHistory()
  const handleNextStep = () => {
    history.push(`/offre/${offerId}/v3/creation/individuelle/confirmation`)
  }
  const handlePreviousStep = () => {
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

  return (
    <>
      {isCreation && <BannerSummary />}
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
                  to={`/offre/${offerId}/individuel/creation/stocks`}
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
                <ButtonLink variant={ButtonVariant.PRIMARY} to={backOfferUrl}>
                  Voir la liste des offres
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
