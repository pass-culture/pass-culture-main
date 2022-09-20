import React, { useEffect, useState } from 'react'
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
import getWizardData from 'routes/OfferIndividualWizard/adapters/getWizardData/getWizardData'
import {
  IDataError,
  IDataLoading,
  IDataSuccess,
} from 'routes/OfferIndividualWizard/OfferIndividualWizard'
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
  const [data, setData] = useState<IDataLoading | IDataSuccess | IDataError>({
    isLoading: true,
  })

  useEffect(() => {
    async function loadData() {
      const response = await getWizardData({
        offerId,
        queryOffererId: offererId,
        isAdmin: currentUser.isAdmin,
      })
      if (response.isOk) {
        setData({ isLoading: false, ...response.payload })
      } else {
        setData({
          isLoading: false,
          error: response.message,
        })
      }
    }
    loadData()
  }, [offerId])

  if (data.isLoading === true) return <Spinner />
  if (data.error !== undefined || data.offer === undefined) {
    notify.error(data.error)
    history.push(homePath)
    return null
  }

  const contextValues: IOfferIndividualContext = {
    offerId: offerId || null,
    offer: data.offer,
    venueList: data.venueList,
    offererNames: data.offererNames,
    categories: data.categoriesData.categories,
    subCategories: data.categoriesData.subCategories,
    reloadOffer: () => {},
  }

  const {
    providerName,
    offerStatus,
    offer: offerData,
    stockThing,
    stockEventList,
    preview,
  } = serializePropsFromOfferIndividual(
    data.offer || null,
    data.categoriesData.categories,
    data.categoriesData.subCategories
  )

  return (
    <OfferIndividualContext.Provider value={contextValues}>
      <SummaryScreen
        offerId={data.offer.id}
        formOfferV2
        providerName={providerName}
        offerStatus={offerStatus}
        isCreation={isCreation}
        offer={offerData}
        stockThing={stockThing}
        stockEventList={stockEventList}
        subCategories={data.categoriesData.subCategories}
        preview={preview}
      />
    </OfferIndividualContext.Provider>
  )
}

export default OfferV2Summary
