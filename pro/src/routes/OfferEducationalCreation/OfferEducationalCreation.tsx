import React, { useEffect, useState } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
// @debt deprecated "Mathilde: should not import utility from legacy page"
import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import {
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  Mode,
  setInitialFormValues,
} from 'core/OfferEducational'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import getCollectiveOfferFormDataApdater from 'core/OfferEducational/adapters/getCollectiveOfferFormDataAdapter'
import CollectiveOfferLayout from 'new_components/CollectiveOfferLayout'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import OfferEducationalScreen from 'screens/OfferEducational'
import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'

import postCollectiveOfferAdapter from './adapters/postCollectiveOfferAdapter'

type AsyncScreenProps = Pick<
  IOfferEducationalProps,
  'categories' | 'userOfferers' | 'domainsOptions'
>

const OfferEducationalCreation = (): JSX.Element => {
  const history = useHistory()
  const location = useLocation()

  const [isReady, setIsReady] = useState<boolean>(false)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)
  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(DEFAULT_EAC_FORM_VALUES)

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)

  const notify = useNotification()

  const createOffer = async (offer: IOfferEducationalFormValues) => {
    const { payload, isOk, message } = await postCollectiveOfferAdapter({
      offer,
    })

    if (!isOk) {
      return notify.error(message)
    }

    history.push(`/offre/${payload.collectiveOfferId}/collectif/stocks`)
  }

  useEffect(() => {
    if (!isReady) {
      const loadData = async () => {
        const result = await getCollectiveOfferFormDataApdater({ offererId })

        if (!result.isOk) {
          notify.error(result.message)
        }

        const { categories, offerers, domains } = result.payload

        setScreenProps({
          categories: categories,
          userOfferers: offerers,
          domainsOptions: domains,
        })

        setInitialValues(values =>
          setInitialFormValues(values, offerers, offererId, venueId)
        )

        setIsReady(true)
      }

      loadData()
    }
  }, [isReady, venueId, offererId])

  return (
    <CollectiveOfferLayout
      breadCrumpProps={{
        activeStep: OfferBreadcrumbStep.DETAILS,
        isCreatingOffer: true,
      }}
      title="Créer une nouvelle offre collective"
    >
      {isReady && screenProps ? (
        <>
          <OfferEducationalScreen
            {...screenProps}
            getIsOffererEligible={canOffererCreateCollectiveOfferAdapter}
            initialValues={initialValues}
            mode={Mode.CREATION}
            onSubmit={createOffer}
          />
          <RouteLeavingGuardOfferCreation isCollectiveFlow />
        </>
      ) : (
        <Spinner />
      )}
    </CollectiveOfferLayout>
  )
}

export default OfferEducationalCreation
