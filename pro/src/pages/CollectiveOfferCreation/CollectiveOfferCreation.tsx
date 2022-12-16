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
import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'
import Spinner from 'ui-kit/Spinner/Spinner'

type AsyncScreenProps = Pick<
  IOfferEducationalProps,
  'categories' | 'userOfferers' | 'domainsOptions'
>

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

  const [isReady, setIsReady] = useState<boolean>(false)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)
  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(DEFAULT_EAC_FORM_VALUES)

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)
  const notify = useNotification()

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

        const { categories, offerers, domains, initialValues } = result.payload

        setScreenProps({
          categories: categories,
          userOfferers: offerers,
          domainsOptions: domains,
        })

        setInitialValues(values =>
          setInitialFormValues(
            { ...values, ...initialValues },
            offerers,
            initialValues.offererId || offererId,
            initialValues.venueId || venueId
          )
        )

        setIsReady(true)
      }

      loadData()
    }
  }, [isReady, venueId, offererId])

  return isReady && screenProps ? (
    <>
      <OfferEducationalScreen
        {...screenProps}
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
  ) : (
    <Spinner />
  )
}

export default CollectiveOfferCreation
