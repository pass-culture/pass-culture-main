import React, { useEffect, useState } from 'react'
import { useHistory, useParams } from 'react-router'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { OFFER_FORM_STEP_IDS, useOfferFormSteps } from 'core/Offers'
import {
  getOfferIndividualAdapter,
  useGetCategories,
} from 'core/Offers/adapters'
import { IOfferIndividual } from 'core/Offers/types'
import { useHomePath } from 'hooks'
import Breadcrumb, { BreadcrumbStyle } from 'new_components/Breadcrumb'
import { OfferFormLayout } from 'new_components/OfferFormLayout'
import { OfferIndividualCreationInformations as InformationsRoute } from 'routes/OfferIndividualCreationInformations'
import { OfferIndividualCreationStocks as StockRoute } from 'routes/OfferIndividualCreationStocks'
import { OfferIndividualSummary as OfferSummaryRoute } from 'routes/OfferIndividualSummary'

const OfferIndividualCreation = (): JSX.Element | null => {
  const notify = useNotification()
  const history = useHistory()
  const homePath = useHomePath()

  const { offerId } = useParams<{ offerId: string }>()
  const [offerIsLoading, setOfferIsLoading] = useState<boolean>(true)
  const [offer, setOffer] = useState<IOfferIndividual | undefined>()

  useEffect(() => {
    async function loadOffer() {
      const response = await getOfferIndividualAdapter(offerId)
      if (response.isOk) {
        setOffer(response.payload)
      } else {
        notify.error(response.message)
        history.push(homePath)
      }
      setOfferIsLoading(false)
    }
    if (offerId) {
      loadOffer()
    } else {
      setOffer(undefined)
      setOfferIsLoading(false)
    }
  }, [offerId])

  const {
    data: categoriesData,
    isLoading: categoriesIsLoading,
    error: categoriesError,
  } = useGetCategories()
  const { currentStep, stepList } = useOfferFormSteps(offer)

  if (categoriesError !== undefined) {
    const loadingError = [categoriesError].find(error => error !== undefined)
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
          <InformationsRoute offer={offer} />
        )}
        {offer && currentStep.id === OFFER_FORM_STEP_IDS.STOCKS && (
          <StockRoute offer={offer} />
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
