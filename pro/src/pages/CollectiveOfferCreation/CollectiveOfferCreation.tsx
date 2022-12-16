import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import RouteLeavingGuardCollectiveOfferCreation from 'components/RouteLeavingGuardCollectiveOfferCreation'
import {
  CollectiveOffer,
  CollectiveOfferTemplate,
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  Mode,
  setInitialFormValues,
} from 'core/OfferEducational'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import getCollectiveOfferFormDataAdapter from 'core/OfferEducational/adapters/getCollectiveOfferFormDataAdapter'
import useNotification from 'hooks/useNotification'
import { queryParamsFromOfferer } from 'pages/Offers/utils/queryParamsFromOfferer'
import OfferEducationalScreen from 'screens/OfferEducational'
import useOfferEducationalFormData from 'screens/OfferEducational/useOfferEducationalFormData'
import Spinner from 'ui-kit/Spinner/Spinner'

interface CollectiveOfferCreationProps {
  offer?: CollectiveOffer | CollectiveOfferTemplate
  setOffer: (offer: CollectiveOffer | CollectiveOfferTemplate) => void
  isTemplate?: boolean
}

const CollectiveOfferCreation = ({
  offer,
  setOffer,
  isTemplate = false,
}: CollectiveOfferCreationProps): JSX.Element => {
  const location = useLocation()

  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(DEFAULT_EAC_FORM_VALUES)

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)
  const notify = useNotification()
  const { isReady, ...offerEducationalFormData } = useOfferEducationalFormData(
    offererId,
    offer
  )

  useEffect(() => {
    if (!isReady) {
      const loadData = async () => {
        const result = await getCollectiveOfferFormDataAdapter({
          offererId,
          offer,
        })

        if (!result.isOk) {
          notify.error(result.message)
        }

        const { offerers, initialValues } = result.payload

        setInitialValues(values =>
          setInitialFormValues(
            { ...values, ...initialValues },
            offerers,
            initialValues.offererId || offererId,
            initialValues.venueId || venueId
          )
        )
      }

      loadData()
    }
  }, [isReady, venueId, offererId])

  if (!isReady) {
    return <Spinner />
  }

  return (
    <>
      <OfferEducationalScreen
        categories={offerEducationalFormData.categories}
        userOfferers={offerEducationalFormData.offerers}
        domainsOptions={offerEducationalFormData.domains}
        offer={offer}
        setOffer={setOffer}
        getIsOffererEligible={canOffererCreateCollectiveOfferAdapter}
        initialValues={initialValues}
        mode={Mode.CREATION}
        isTemplate={isTemplate}
        isOfferCreated={offer !== undefined}
      />
      <RouteLeavingGuardCollectiveOfferCreation />
    </>
  )
}

export default CollectiveOfferCreation
