import React from 'react'
import { useHistory, useParams } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  CollectiveOffer,
  DEFAULT_EAC_STOCK_FORM_VALUES,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import { useAdapter } from 'hooks'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import postCollectiveStockAdapter from 'routes/OfferEducationalStockCreation/adapters/postCollectiveStock'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

const CollectiveOfferStockCreationFromTemplate = (): JSX.Element | null => {
  const { offerId } = useParams<{ offerId: string }>()
  const history = useHistory()
  const notify = useNotification()

  const handleSubmitStock = async (
    offer: CollectiveOffer,
    values: OfferEducationalStockFormValues
  ) => {
    const response = await postCollectiveStockAdapter({
      offer,
      values,
    })
    if (!response.isOk) {
      return notify.error(response.message)
    }
    history.push(`/offre/duplication/${offerId}/collectif/visibilite`)
  }

  const { isLoading, error, data } = useAdapter(() =>
    getCollectiveOfferAdapter(offerId)
  )

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
      title="Créer une offre collective"
      subTitle={data.name}
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
