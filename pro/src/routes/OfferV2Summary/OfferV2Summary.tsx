import React from 'react'
import { useHistory, useParams } from 'react-router-dom'

import useCurrentUser from 'components/hooks/useCurrentUser'
import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { useHomePath } from 'hooks'
import useIsCreation from 'new_components/OfferIndividualStepper/hooks/useIsCreation'
import { useGetData } from 'routes/OfferIndividualWizard/hooks'
import { useGetDataAdmin } from 'routes/OfferIndividualWizard/hooks/useGetDataAdmin'
import { serializePropsFromOfferIndividual } from 'routes/OfferIndividualWizard/Summary/serializer'
import { Summary as SummaryScreen } from 'screens/OfferIndividual/Summary'

const OfferV2Summary = (): JSX.Element | null => {
  const isCreation = useIsCreation()
  const homePath = useHomePath()
  const notify = useNotification()
  const history = useHistory()
  const { currentUser } = useCurrentUser()

  const { offerId, structure: offererId } = useParams<{
    offerId: string
    structure: string
  }>()
  const { data, isLoading, loadingError, reloadOffer } = currentUser.isAdmin
    ? useGetDataAdmin(offerId, offererId)
    : useGetData(offerId)

  if (isLoading === true) return <Spinner />
  if (loadingError !== undefined || data.offer === undefined) {
    notify.error(loadingError)
    history.push(homePath)
    return null
  }

  const {
    offer,
    venueList,
    offererNames,
    categoriesData: { categories, subCategories },
  } = data

  const contextValues: IOfferIndividualContext = {
    offerId: offerId,
    offer: offer,
    venueList,
    offererNames,
    categories,
    subCategories,
    reloadOffer: () => reloadOffer(),
  }

  const {
    providerName,
    offerStatus,
    offer: offerData,
    stockThing,
    stockEventList,
    preview,
  } = serializePropsFromOfferIndividual(offer, categories, subCategories)

  return (
    <OfferIndividualContext.Provider value={contextValues}>
      <SummaryScreen
        offerId={offer.id}
        formOfferV2
        providerName={providerName}
        offerStatus={offerStatus}
        isCreation={isCreation}
        offer={offerData}
        stockThing={stockThing}
        stockEventList={stockEventList}
        subCategories={subCategories}
        preview={preview}
      />
    </OfferIndividualContext.Provider>
  )
}

export default OfferV2Summary
