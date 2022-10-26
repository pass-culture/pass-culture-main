import React from 'react'
import { useHistory, useParams } from 'react-router-dom'

import {
  CollectiveOffer,
  DEFAULT_EAC_STOCK_FORM_VALUES,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import useNotification from 'hooks/useNotification'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import postCollectiveStockAdapter from 'routes/CollectiveOfferStockCreation/adapters/postCollectiveStock'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

interface CollectiveOfferStockCreationFromTemplateProps {
  offer: CollectiveOffer
}

const CollectiveOfferStockCreationFromTemplate = ({
  offer,
}: CollectiveOfferStockCreationFromTemplateProps): JSX.Element | null => {
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
    history.push(`/offre/duplication/collectif/${offerId}/visibilite`)
  }

  return (
    <>
      <OfferEducationalStockScreen
        initialValues={DEFAULT_EAC_STOCK_FORM_VALUES}
        isCreatingFromTemplate
        mode={Mode.CREATION}
        offer={offer}
        onSubmit={handleSubmitStock}
      />
      <RouteLeavingGuardOfferCreation />
    </>
  )
}

export default CollectiveOfferStockCreationFromTemplate
