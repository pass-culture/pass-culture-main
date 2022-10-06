import React from 'react'
import { useParams } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  DEFAULT_EAC_STOCK_FORM_VALUES,
  GetStockOfferSuccessPayload,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import useGetStockCollectiveOfferAdapter from 'core/OfferEducational/adapters/useGetStockCollectiveOfferAdapter'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import postCollectiveStockAdapter from 'routes/OfferEducationalStockCreation/adapters/postCollectiveStock'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

const CollectiveOfferStockCreationFromTemplate = (): JSX.Element | null => {
  const { offerId } = useParams<{ offerId: string }>()
  const notify = useNotification()

  const handleSubmitStock = async (
    offer: GetStockOfferSuccessPayload,
    values: OfferEducationalStockFormValues
  ) => {
    const response = await postCollectiveStockAdapter({
      offer,
      values,
    })

    if (!response.isOk) {
      return notify.error(response.message)
    }
  }

  const { isLoading, error, data } = useGetStockCollectiveOfferAdapter(offerId)

  if (error) {
    notify.error(error.message)
    return null
  }
  if (isLoading) {
    return <Spinner />
  }

  return (
    <CollectiveOfferLayout
      breadCrumpProps={{
        activeStep: OfferBreadcrumbStep.STOCKS,
        isCreatingOffer: true,
      }}
      title="Créer une nouvelle offre collective"
      subTitle={data.name || ''}
    >
      <OfferEducationalStockScreen
        initialValues={DEFAULT_EAC_STOCK_FORM_VALUES}
        isCreatingFromTemplate
        mode={Mode.CREATION}
        offer={data}
        onSubmit={handleSubmitStock}
      />
      <RouteLeavingGuardOfferCreation isCollectiveFlow />
    </CollectiveOfferLayout>
  )
}

export default CollectiveOfferStockCreationFromTemplate
