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
  getOfferAdapter,
  setInitialFormValues,
} from 'core/OfferEducational'
import { Offer } from 'custom_types/offer'
import OfferEducationalScreen from 'screens/OfferEducational'
import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'
import { Title } from 'ui-kit'

import patchOfferAdapter from './adapters/patchOfferAdapter'
import { computeInitialValuesFromOffer } from './utils/computeInitialValuesFromOffer'

type AsyncScreenProps = Pick<
  IOfferEducationalProps,
  'educationalCategories' | 'educationalSubCategories' | 'userOfferers'
>

const isLoadOfferSuccess = (response: {
  isOk: boolean
  message: string | null
  payload: { offer: Offer | null }
}): response is { isOk: boolean; message: null; payload: { offer: Offer } } =>
  response.isOk === true

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
        const [offerResult, ...results] = await Promise.all([
          getOfferAdapter(offerId),
          getCategoriesAdapter(null),
          getOfferersAdapter(null),
        ])

        if (results.some(res => !res.isOk)) {
          notify.error(results?.find(res => !res.isOk)?.message)
        }

        if (!isLoadOfferSuccess(offerResult)) {
          return notify.error(offerResult.message)
        }

        const offer = offerResult.payload.offer
        const [categories, offerers] = results

        const offerSubcategory =
          categories.payload.educationalSubCategories.filter(
            ({ id }) => offer.subcategoryId === id
          )

        const offerCategory = offerSubcategory[0]
          ? categories.payload.educationalCategories.filter(
              ({ id }) => offerSubcategory[0].categoryId === id
            )
          : []

        const userOfferers = offerers.payload.filter(offerer =>
          offerer.managedVenues.map(venue => venue.id).includes(offer.venueId)
        )

        const initialValuesFromOffer = computeInitialValuesFromOffer(
          offer,
          offerCategory[0].id,
          offerSubcategory[0].id
        )

        setScreenProps({
          educationalCategories: offerCategory,
          educationalSubCategories: offerSubcategory,
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

  return isReady && screenProps ? (
    <>
      <Title level={1}>Éditer une offre</Title>
      <OfferEducationalScreen
        {...screenProps}
        initialValues={initialValues}
        mode={Mode.EDITION}
        notify={notify}
        onSubmit={editOffer}
      />
    </>
  ) : (
    <Spinner />
  )
}

export default withTracking('Offer')(OfferEducationalEdition)
