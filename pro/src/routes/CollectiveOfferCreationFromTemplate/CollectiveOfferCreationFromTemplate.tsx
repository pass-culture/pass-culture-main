import React, { useEffect, useState } from 'react'
import { useHistory, useParams } from 'react-router'

import {
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  Mode,
  setInitialFormValues,
} from 'core/OfferEducational'
import getCollectiveOfferFormDataApdater from 'core/OfferEducational/adapters/getCollectiveOfferFormDataAdapter'
import getCollectiveOfferTemplateAdapter from 'core/OfferEducational/adapters/getCollectiveOfferTemplateAdapter'
import postCollectiveOfferAdapter from 'core/OfferEducational/adapters/postCollectiveOfferAdapter'
import useNotification from 'hooks/useNotification'
import { RouteLeavingGuardOfferCreation } from 'new_components/RouteLeavingGuardOfferCreation'
import OfferEducational from 'screens/OfferEducational'
import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'
import Spinner from 'ui-kit/Spinner/Spinner'

type AsyncScreenProps = Pick<
  IOfferEducationalProps,
  'domainsOptions' | 'userOfferers' | 'categories'
>

const CollectiveOfferCreationFromTemplate = () => {
  const { templateId } = useParams<{ templateId: string }>()
  const notify = useNotification()
  const history = useHistory()

  const [isLoading, setIsLoading] = useState(true)
  const [initialValues, setInitialValues] = useState(DEFAULT_EAC_FORM_VALUES)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)

  const handleSubmit = async (offer: IOfferEducationalFormValues) => {
    const { isOk, message, payload } = await postCollectiveOfferAdapter({
      offer,
      offerTemplateId: templateId,
    })

    if (!isOk) {
      return notify.error(message)
    }
    history.push(`/offre/duplication/collectif/${payload.offerId}/stocks`)
  }

  useEffect(() => {
    const loadData = async () => {
      const offerTemplateResponse = await getCollectiveOfferTemplateAdapter(
        templateId
      )

      if (!offerTemplateResponse.isOk) {
        return notify.error(offerTemplateResponse.message)
      }

      const result = await getCollectiveOfferFormDataApdater({
        offererId: offerTemplateResponse.payload.venue.managingOffererId,
        offer: offerTemplateResponse.payload,
      })

      if (!result.isOk) {
        notify.error(result.message)
      }

      const { categories, offerers, domains, initialValues } = result.payload

      setScreenProps({
        userOfferers: offerers,
        domainsOptions: domains,
        categories,
      })

      setInitialValues(values =>
        setInitialFormValues(
          {
            ...values,
            ...initialValues,
          },
          offerers,
          offerers[0].id,
          offerTemplateResponse.payload.venueId
        )
      )

      setIsLoading(false)
    }

    loadData()
  }, [])

  if (isLoading || !screenProps) {
    return <Spinner />
  }

  return (
    <>
      <OfferEducational
        {...screenProps}
        initialValues={initialValues}
        onSubmit={handleSubmit}
        mode={Mode.CREATION}
      />
      <RouteLeavingGuardOfferCreation />
    </>
  )
}

export default CollectiveOfferCreationFromTemplate
