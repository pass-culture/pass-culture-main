import React, { useCallback, useEffect, useState } from 'react'
import { useHistory, useLocation, useParams } from 'react-router-dom'

import Spinner from 'components/layout/Spinner'
import {
  IOfferIndividualContext,
  OfferIndividualContext,
} from 'context/OfferIndividualContext'
import { getOfferIndividualAdapter } from 'core/Offers/adapters'
import { useHomePath } from 'hooks'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import useIsCompletingDraft from 'new_components/OfferIndividualStepper/hooks/useIsCompletingDraft'
import useIsCreation from 'new_components/OfferIndividualStepper/hooks/useIsCreation'
import getWizardData from 'routes/OfferIndividualWizard/adapters/getWizardData/getWizardData'
import {
  IDataError,
  IDataLoading,
  IDataSuccess,
} from 'routes/OfferIndividualWizard/OfferIndividualWizard'
import { serializePropsFromOfferIndividual } from 'routes/OfferIndividualWizard/Summary/serializer'
import { Summary as SummaryScreen } from 'screens/OfferIndividual/Summary'
import { parse } from 'utils/query-string'

const OfferV2Summary = (): JSX.Element | null => {
  const isCreation = useIsCreation()
  const isDraft = useIsCompletingDraft()
  const homePath = useHomePath()
  const notify = useNotification()
  const history = useHistory()
  const { currentUser } = useCurrentUser()
  const [data, setData] = useState<IDataLoading | IDataSuccess | IDataError>({
    isLoading: true,
  })

  const { offerId } = useParams<{ offerId: string }>()
  const { search } = useLocation()
  const { structure: offererId } = parse(search)

  const loadOffer = useCallback(async () => {
    const response = await getOfferIndividualAdapter(offerId)
    if (response.isOk) {
      setData({
        offererNames: [],
        venueList: [],
        categoriesData: {
          categories: [],
          subCategories: [],
        },
        isLoading: data.isLoading,
        offer: response.payload,
        error: undefined,
      })
      return Promise.resolve(response.payload)
    }
    notify.error(response.message)
    history.push(homePath)
    return Promise.resolve()
  }, [offerId])
  useEffect(() => {
    offerId && loadOffer()
  }, [offerId])

  useEffect(() => {
    async function loadData() {
      const response = await getWizardData({
        offer: data.offer,
        queryOffererId: offererId,
        isAdmin: currentUser.isAdmin,
      })
      if (response.isOk) {
        setData({ isLoading: false, offer: data.offer, ...response.payload })
      } else {
        setData({
          isLoading: false,
          error: response.message,
        })
      }
    }
    ;(!offerId || data.offer) && loadData()
  }, [offerId, data.offer])

  if (data.isLoading === true) return <Spinner />
  if (data.error !== undefined || data.offer === undefined) {
    data.error !== undefined && notify.error(data.error)
    history.push(homePath)
    return null
  }

  const contextValues: IOfferIndividualContext = {
    offerId: offerId || null,
    offer: data.offer || null,
    venueList: data.venueList,
    offererNames: data.offererNames,
    categories: data.categoriesData.categories,
    subCategories: data.categoriesData.subCategories,
    reloadOffer: () => loadOffer(),
  }

  const {
    providerName,
    offerStatus,
    offer: offerData,
    stockThing,
    stockEventList,
    preview,
  } = serializePropsFromOfferIndividual(
    data.offer,
    data.categoriesData.categories,
    data.categoriesData.subCategories
  )

  return (
    <OfferIndividualContext.Provider value={contextValues}>
      <SummaryScreen
        offerId={offerId}
        formOfferV2
        providerName={providerName}
        offerStatus={offerStatus}
        isCreation={isCreation}
        isDraft={isDraft}
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
