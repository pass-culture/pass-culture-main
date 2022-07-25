import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import { matchPath, useLocation } from 'react-router-dom'

import { IOfferIndividual } from 'core/Offers/types'
import React from 'react'
import { Summary as SummaryScreen } from 'screens/OfferIndividual/Summary'
import { serializePropsFromOfferIndividual } from '.'

interface IOfferIndividualSummaryProps {
  formOfferV2?: boolean
  offer: IOfferIndividual
  categories: IOfferCategory[]
  subCategories: IOfferSubCategory[]
}

const OfferIndividualSummary = ({
  formOfferV2 = false,
  offer,
  categories,
  subCategories,
}: IOfferIndividualSummaryProps): JSX.Element | null => {
  const location = useLocation()
  const isCreation =
    matchPath(
      location.pathname,
      '/offre/:offer_id/individuel/creation/recapitulatif'
    ) !== null

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
