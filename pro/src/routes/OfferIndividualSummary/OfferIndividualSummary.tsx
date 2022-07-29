import React from 'react'
import { matchPath, useLocation, useHistory, useParams } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import { useGetCategories, useGetOfferIndividual } from 'core/Offers/adapters'
import { useHomePath } from 'hooks'
import { Summary as SummaryScreen } from 'screens/OfferIndividual/Summary'

import { serializePropsFromOfferIndividual } from '.'

interface IOfferIndividualSummaryProps {
  formOfferV2?: boolean
}

const OfferIndividualSummary = ({
  formOfferV2 = false,
}: IOfferIndividualSummaryProps): JSX.Element | null => {
  const notify = useNotification()
  const history = useHistory()
  const homePath = useHomePath()
  const location = useLocation()
  const isCreation =
    matchPath(
      location.pathname,
      '/offre/:offer_id/individuel/creation/recapitulatif'
    ) !== null

  const { offerId } = useParams<{ offerId: string }>()
  const {
    data: offer,
    isLoading: offerIsLoading,
    error: offerError,
  } = useGetOfferIndividual(offerId)
  const {
    data: categoriesData,
    isLoading: categoriesIsLoading,
    error: categoriesError,
  } = useGetCategories()

  if (categoriesError !== undefined || offerError !== undefined) {
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

  const { categories, subCategories } = categoriesData

  const {
    providerName,
    offerStatus,
    offer: offerData,
    stockThing,
    stockEventList,
    preview,
  } = serializePropsFromOfferIndividual(offer, categories, subCategories)

  return (
    <SummaryScreen
      offerId={offer.id}
      formOfferV2={formOfferV2}
      providerName={providerName}
      offerStatus={offerStatus}
      isCreation={isCreation}
      offer={offerData}
      stockThing={stockThing}
      stockEventList={stockEventList}
      subCategories={subCategories}
      preview={preview}
    />
  )
}

export default OfferIndividualSummary
