import React, { useEffect, useState } from 'react'
import { useHistory, useLocation } from 'react-router'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
// @debt deprecated "Mathilde: should not import utility from legacy page"
import { queryParamsFromOfferer } from 'components/pages/Offers/utils/queryParamsFromOfferer'
import {
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  Mode,
  setInitialFormValues,
  getCategoriesAdapter,
  getOfferersAdapter,
} from 'core/OfferEducational'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import RouteLeavingGuardOfferCreation from 'new_components/RouteLeavingGuardOfferCreation'
import OfferEducationalScreen from 'screens/OfferEducational'
import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'

import { getIsOffererEligibleAdapter } from './adapters'
import postOfferAdapter from './adapters/postOfferAdapter'

type AsyncScreenProps = Pick<
  IOfferEducationalProps,
  'educationalCategories' | 'educationalSubCategories' | 'userOfferers'
>

const OfferEducationalCreation = (): JSX.Element => {
  const history = useHistory()
  const location = useLocation()
  const isShowcaseFeatureEnabled = useActiveFeature('ENABLE_EAC_SHOWCASE_OFFER')

  const [isReady, setIsReady] = useState<boolean>(false)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)
  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(DEFAULT_EAC_FORM_VALUES)

  const { structure: offererId, lieu: venueId } =
    queryParamsFromOfferer(location)

  const notify = useNotification()

  const createOffer = async (offer: IOfferEducationalFormValues) => {
    const { payload, isOk, message } = await postOfferAdapter(offer)

    if (!isOk) {
      return notify.error(message)
    }

    history.push(`/offre/${payload.offerId}/collectif/stocks`)
  }

  useEffect(() => {
    if (!isReady) {
      const loadData = async () => {
        const results = await Promise.all([
          getCategoriesAdapter(null),
          getOfferersAdapter(offererId),
        ])

        if (results.some(res => !res.isOk)) {
          // handle error with notification at some point
          console.error(results?.find(res => !res.isOk)?.message)
        }

        const [categories, offerers] = results

        setScreenProps({
          educationalCategories: categories.payload.educationalCategories,
          educationalSubCategories: categories.payload.educationalSubCategories,
          userOfferers: offerers.payload,
        })

        setInitialValues(values =>
          setInitialFormValues(values, offerers.payload, offererId, venueId)
        )

        setIsReady(true)
      }

      loadData()
    }
  }, [isReady, venueId, offererId])

  return (
    <OfferEducationalLayout
      activeStep={OfferBreadcrumbStep.DETAILS}
      isCreatingOffer
      title="Créer une nouvelle offre scolaire"
    >
      {isReady && screenProps ? (
        <>
          <OfferEducationalScreen
            {...screenProps}
            getIsOffererEligible={getIsOffererEligibleAdapter}
            initialValues={initialValues}
            isShowcaseFeatureEnabled={isShowcaseFeatureEnabled}
            mode={Mode.CREATION}
            notify={notify}
            onSubmit={createOffer}
          />
          <RouteLeavingGuardOfferCreation isCollectiveFlow />
        </>
      ) : (
        <Spinner />
      )}
    </OfferEducationalLayout>
  )
}

export default OfferEducationalCreation
