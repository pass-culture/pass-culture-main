import React from 'react'
import { useHistory, useParams } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  CollectiveOffer,
  DEFAULT_EAC_STOCK_FORM_VALUES,
  EducationalOfferType,
  Mode,
  OfferEducationalStockFormValues,
} from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { useAdapter } from 'hooks'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import OfferEducationalStockScreen from 'screens/OfferEducationalStock'

import postCollectiveOfferTemplateAdapter from './adapters/postCollectiveOfferTemplate'
import postCollectiveStockAdapter from './adapters/postCollectiveStock'

const OfferEducationalStockCreation = (): JSX.Element | null => {
  const { offerId } = useParams<{ offerId: string }>()
  const notify = useNotification()
  const history = useHistory()

  const handleSubmitStock = async (
    offer: CollectiveOffer,
    values: OfferEducationalStockFormValues
  ) => {
    let isOk: boolean
    let message: string | null
    let payload: { id: string } | null
    const isTemplate =
      values.educationalOfferType === EducationalOfferType.SHOWCASE

    if (isTemplate) {
      const response = await postCollectiveOfferTemplateAdapter({
        offerId: offer.id,
        values,
      })
      isOk = response.isOk
      message = response.message
      payload = response.payload
    } else {
      const response = await postCollectiveStockAdapter({
        offer,
        values,
      })
      isOk = response.isOk
      message = response.message
      payload = response.payload
    }

    if (!isOk) {
      return notify.error(message)
    }

    let url = `/offre/${computeURLCollectiveOfferId(
      isTemplate && payload ? payload.id : offer.id,
      isTemplate
    )}/collectif`

    if (!isTemplate) {
      url = `${url}/visibilite`
    } else {
      url = `${url}/confirmation`
    }
    history.push(url)
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
      title="Créer une nouvelle offre collective"
      subTitle={data.name}
    >
      <>
        <OfferEducationalStockScreen
          initialValues={DEFAULT_EAC_STOCK_FORM_VALUES}
          mode={Mode.CREATION}
          offer={data}
          onSubmit={handleSubmitStock}
        />
        <RouteLeavingGuardOfferCreation isCollectiveFlow />
      </>
    </CollectiveOfferLayout>
  )
}

export default OfferEducationalStockCreation
