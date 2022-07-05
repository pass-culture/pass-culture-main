import Breadcrumb, { BreadcrumbStyle } from 'new_components/Breadcrumb'
import { OFFER_FORM_STEP_IDS, useOfferFormSteps } from 'core/Offers'
import { useGetCategories, useGetOffer } from 'core/Offers/adapters'
import { useHistory, useParams } from 'react-router'

import { OfferIndividualCreationInformations as InformationsRoute } from 'routes/OfferIndividualCreationInformations'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import { OfferIndividualSummary as OfferSummaryRoute } from 'routes/OfferIndividualSummary'
import React from 'react'
import Spinner from 'components/layout/Spinner'
import { OfferIndividualCreationStocks as StockRoute } from 'routes/OfferIndividualCreationStocks'
import { useHomePath } from 'hooks'
import useNotification from 'components/hooks/useNotification'

const OfferIndividualCreation = (): JSX.Element | null => {
  const notify = useNotification()
  const history = useHistory()
  const homePath = useHomePath()

  const { offerId } = useParams<{ offerId: string }>()
  const {
    data: offer,
    isLoading: offerIsLoading,
    error: offerError,
  } = useGetOffer(offerId)
  const {
    data: categoriesData,
    isLoading: categoriesIsLoading,
    error: categoriesError,
  } = useGetCategories()
  const { currentStep, stepList } = useOfferFormSteps(offer)

  if (categoriesError !== undefined || (offerId && offerError !== undefined)) {
    const loadingError = [categoriesError, offerError].find(
      error => error !== undefined
    )
    if (loadingError !== undefined) {
      notify.error(loadingError.message)
      history.push(homePath)
    }
    return null
  }

  if (offerIsLoading || categoriesIsLoading) {
    return <Spinner />
  }

  return (
    <OfferFormLayout>
      <OfferFormLayout.TitleBlock>
        <h1>Créer une offre</h1>
      </OfferFormLayout.TitleBlock>
      {offer && currentStep.id !== OFFER_FORM_STEP_IDS.INFORMATIONS && (
        <OfferFormLayout.TitleBlock>
          <h4>{offer.name}</h4>
        </OfferFormLayout.TitleBlock>
      )}
      <OfferFormLayout.Stepper>
        <Breadcrumb
          activeStep={currentStep.id}
          steps={stepList}
          styleType={BreadcrumbStyle.TAB}
        />
      </OfferFormLayout.Stepper>

      <OfferFormLayout.Content>
        {currentStep.id === OFFER_FORM_STEP_IDS.INFORMATIONS && (
          <InformationsRoute />
        )}
        {offerId && currentStep.id === OFFER_FORM_STEP_IDS.STOCKS && (
          <StockRoute />
        )}
        {offer && currentStep.id === OFFER_FORM_STEP_IDS.SUMMARY && (
          <OfferSummaryRoute
            offer={offer}
            categories={categoriesData.categories}
            subCategories={categoriesData.subCategories}
          />
        )}
      </OfferFormLayout.Content>
    </OfferFormLayout>
  )
}

export default OfferIndividualCreation
