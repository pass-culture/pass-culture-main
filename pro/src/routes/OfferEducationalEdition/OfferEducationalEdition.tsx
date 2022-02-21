import React, { useCallback, useEffect, useState } from 'react'
import { useHistory, useParams } from 'react-router'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  IOfferEducationalFormValues,
  DEFAULT_EAC_FORM_VALUES,
  Mode,
  getCategoriesAdapter,
  getOfferersAdapter,
  setInitialFormValues,
  patchIsOfferActiveAdapter,
  cancelActiveBookingsAdapter,
} from 'core/OfferEducational'
import { Offer } from 'custom_types/offer'
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

const OfferEducationalEdition = (): JSX.Element => {
  const { offerId } = useParams<{ offerId: string }>()
  const history = useHistory()
  const isShowcaseFeatureEnabled = useActiveFeature('ENABLE_EAC_SHOWCASE_OFFER')

  const [isReady, setIsReady] = useState<boolean>(false)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)
  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(DEFAULT_EAC_FORM_VALUES)
  const [offer, setOffer] = useState<Offer>()

  const notify = useNotification()

  const editOffer = async (offer: IOfferEducationalFormValues) => {
    const offerResponse = await patchOfferAdapter({
      offerId,
      offer,
      initialValues,
    })

    if (!offerResponse.isOk) {
      return notify.error(offerResponse.message)
    }

    notify.success(offerResponse.message)
    loadData(offerResponse)
  }

  const setIsOfferActive = async (isActive: boolean) => {
    const { isOk, message } = await patchIsOfferActiveAdapter({
      isActive,
      offerId,
    })

    if (!isOk) {
      return notify.error(message)
    }

    notify.success(message)
    setIsReady(false)
  }

  const cancelActiveBookings = async () => {
    const { isOk, message } = await cancelActiveBookingsAdapter({ offerId })

    if (!isOk) {
      return notify.error(message)
    }

    notify.success(message)
    setIsReady(false)
  }

  const loadData = useCallback(
    async (offerResponse: AdapterFailure<null> | AdapterSuccess<Offer>) => {
      if (!offerResponse.isOk) {
        return notify.error(offerResponse.message)
      }

      const offer = offerResponse.payload
      setOffer(offer)
      const offererId = offer.venue.managingOffererId

      const results = await Promise.all([
        getCategoriesAdapter(null),
        getOfferersAdapter(offererId),
      ])

      if (results.some(res => !res.isOk)) {
        notify.error(results?.find(res => !res.isOk)?.message)
      }

      const [categories, offerers] = results

      const offerSubcategory = categories.payload.educationalSubCategories.find(
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
    },
    [notify]
  )

  useEffect(() => {
    if (!isReady) {
      getOfferAdapter(offerId).then(offerResponse => {
        if (offerResponse.isOk && !offerResponse.payload.isEducational) {
          return history.push(`/offre/${offerId}/individuel/edition`)
        }
        loadData(offerResponse)
      })
    }
  }, [isReady, offerId, loadData, history])

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
          cancelActiveBookings={cancelActiveBookings}
          initialValues={initialValues}
          isOfferActive={offer?.isActive}
          isOfferBooked={offer?.isBooked}
          isShowcaseFeatureEnabled={isShowcaseFeatureEnabled}
          mode={Mode.EDITION}
          notify={notify}
          onSubmit={editOffer}
          setIsOfferActive={setIsOfferActive}
        />
      ) : (
        <Spinner />
      )}
    </OfferEducationalLayout>
  )
}

export default OfferEducationalEdition
