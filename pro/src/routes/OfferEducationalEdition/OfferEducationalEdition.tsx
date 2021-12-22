import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router'

import { withTracking } from 'components/hocs'
import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  IOfferEducationalFormValues,
  DEFAULT_EAC_FORM_VALUES,
  Mode,
  getCategoriesAdapter,
  getOfferersAdapter,
  setInitialFormValues,
} from 'core/OfferEducational'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import OfferEducationalScreen from 'screens/OfferEducational'
import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'

import getOfferAdapter from './adapters/getOfferAdapter'
import patchOfferAdapter from './adapters/patchOfferAdapter'
import { computeInitialValuesFromOffer } from './utils/computeInitialValuesFromOffer'

type AsyncScreenProps = Pick<
  IOfferEducationalProps,
  'educationalCategories' | 'educationalSubCategories' | 'userOfferers'
>

const OfferEducationalEdition = ({
  tracking,
}: {
  tracking: { trackEvent: (props: { action: string; name: string }) => void }
}): JSX.Element => {
  const { offerId } = useParams<{ offerId: string }>()

  const [isReady, setIsReady] = useState<boolean>(false)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)
  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(DEFAULT_EAC_FORM_VALUES)

  const notify = useNotification()

  const editOffer = async (offer: IOfferEducationalFormValues) => {
    const { isOk, message } = await patchOfferAdapter({
      offerId,
      offer,
      initialValues,
    })

    if (!isOk) {
      return notify.error(message)
    }

    tracking.trackEvent({ action: 'modifyOffer', name: offerId })

    notify.success(message)
  }

  useEffect(() => {
    if (!isReady) {
      const loadData = async () => {
        const offerResponse = await getOfferAdapter(offerId)

        if (!offerResponse.isOk) {
          return notify.error(offerResponse.message)
        }

        const offer = offerResponse.payload
        const offererId = offer.venue.managingOffererId

        const results = await Promise.all([
          getCategoriesAdapter(null),
          getOfferersAdapter(offererId),
        ])

        if (results.some(res => !res.isOk)) {
          notify.error(results?.find(res => !res.isOk)?.message)
        }

        const [categories, offerers] = results

        const offerSubcategory =
          categories.payload.educationalSubCategories.find(
            ({ id }) => offer.subcategoryId === id
          )

        const offerCategory = offerSubcategory
          ? categories.payload.educationalCategories.find(
              ({ id }) => offerSubcategory.categoryId === id
            )
          : undefined

        const userOfferers = offerers.payload.filter(offerer =>
          offerer.managedVenues.map(venue => venue.id).includes(offer.venueId)
        )

        const initialValuesFromOffer = computeInitialValuesFromOffer(
          offer,
          offerCategory?.id ?? '',
          offerSubcategory?.id ?? ''
        )

        setScreenProps({
          educationalCategories: categories.payload.educationalCategories,
          educationalSubCategories: categories.payload.educationalSubCategories,
          userOfferers,
        })

        setInitialValues(values =>
          setInitialFormValues(
            {
              ...values,
              ...initialValuesFromOffer,
            },
            userOfferers,
            userOfferers[0].id,
            offer.venueId
          )
        )

        setIsReady(true)
      }

      loadData()
    }
  }, [isReady, offerId, notify])

  return (
    <OfferEducationalLayout
      activeStep={OfferBreadcrumbStep.DETAILS}
      isCreatingOffer={false}
      offerId={offerId}
      title="Éditer une offre"
    >
      {isReady && screenProps ? (
        <OfferEducationalScreen
          {...screenProps}
          initialValues={initialValues}
          mode={Mode.EDITION}
          notify={notify}
          onSubmit={editOffer}
        />
      ) : (
        <Spinner />
      )}
    </OfferEducationalLayout>
  )
}

export default withTracking('Offer')(OfferEducationalEdition)
