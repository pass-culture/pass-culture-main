import React, { useCallback, useEffect, useState } from 'react'
import { useHistory, useParams } from 'react-router-dom'

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
  cancelCollectiveBookingAdapter,
  CollectiveOffer,
  CollectiveOfferTemplate,
  extractOfferIdAndOfferTypeFromRouteParams,
} from 'core/OfferEducational'
import { Offer } from 'custom_types/offer'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import OfferEducationalScreen from 'screens/OfferEducational'
import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'

import getCollectiveOfferAdapter from './adapters/getCollectiveOfferAdapter'
import getCollectiveOfferTemplateAdapter from './adapters/getCollectiveOfferTemplateAdapter'
import getOfferAdapter from './adapters/getOfferAdapter'
import patchCollectiveOfferAdapter from './adapters/patchCollectiveOfferAdapter'
import { patchCollectiveOfferTemplateAdapter } from './adapters/patchCollectiveOfferTemplateAdapter'
import patchOfferAdapter from './adapters/patchOfferAdapter'
import { computeInitialValuesFromOffer } from './utils/computeInitialValuesFromOffer'

type AsyncScreenProps = Pick<
  IOfferEducationalProps,
  'educationalCategories' | 'educationalSubCategories' | 'userOfferers'
>

const OfferEducationalEdition = (): JSX.Element => {
  const { offerId: offerIdFromParams } = useParams<{ offerId: string }>()
  const { offerId, isShowcase } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)
  const history = useHistory()
  const enableIndividualAndCollectiveSeparation = useActiveFeature(
    'ENABLE_INDIVIDUAL_AND_COLLECTIVE_OFFER_SEPARATION'
  )
  const isNewModelEnabled = useActiveFeature('ENABLE_NEW_COLLECTIVE_MODEL')

  const [isReady, setIsReady] = useState<boolean>(false)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)
  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(DEFAULT_EAC_FORM_VALUES)
  const [offer, setOffer] = useState<
    Offer | CollectiveOffer | CollectiveOfferTemplate
  >()

  const notify = useNotification()

  const editOffer = useCallback(
    async (offerFormValues: IOfferEducationalFormValues) => {
      if (offer) {
        let patchOfferId = offerId

        if (enableIndividualAndCollectiveSeparation && !isNewModelEnabled) {
          patchOfferId = (offer as CollectiveOffer).offerId || ''
        }

        let patchAdapter
        if (isNewModelEnabled) {
          patchAdapter = isShowcase
            ? patchCollectiveOfferTemplateAdapter
            : patchCollectiveOfferAdapter
        } else {
          patchAdapter = patchOfferAdapter
        }
        const offerResponse = await patchAdapter({
          offerId: patchOfferId,
          offer: offerFormValues,
          initialValues,
        })

        if (!offerResponse.isOk) {
          return notify.error(offerResponse.message)
        }

        notify.success(offerResponse.message)
        loadData(offerResponse)
      }
    },
    [offer]
  )

  const setIsOfferActive = async (isActive: boolean) => {
    const patchOfferId =
      enableIndividualAndCollectiveSeparation && !isNewModelEnabled
        ? (offer as CollectiveOffer).offerId || ''
        : offerId
    const { isOk, message } = await patchIsOfferActiveAdapter({
      isActive,
      offerId: patchOfferId,
    })

    if (!isOk) {
      return notify.error(message)
    }

    notify.success(message)
    setIsReady(false)
  }

  const cancelActiveBookings = async () => {
    const patchOfferId =
      enableIndividualAndCollectiveSeparation && !isNewModelEnabled
        ? offerId
        : offerId
    const cancelAdapter = isNewModelEnabled
      ? cancelCollectiveBookingAdapter
      : cancelActiveBookingsAdapter
    const { isOk, message } = await cancelAdapter({
      offerId: patchOfferId,
    })

    if (!isOk) {
      return notify.error(message)
    }

    notify.success(message)
    setIsReady(false)
  }

  const loadData = useCallback(
    async (
      offerResponse:
        | AdapterFailure<null>
        | AdapterSuccess<Offer>
        | AdapterSuccess<CollectiveOffer>
        | AdapterSuccess<CollectiveOfferTemplate>
    ) => {
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
      const _loadData = async () => {
        let offerResponse:
          | AdapterFailure<null>
          | AdapterSuccess<Offer>
          | AdapterSuccess<CollectiveOffer>
          | AdapterSuccess<CollectiveOfferTemplate>

        if (enableIndividualAndCollectiveSeparation) {
          const getOfferAdapter = isShowcase
            ? getCollectiveOfferTemplateAdapter
            : getCollectiveOfferAdapter
          offerResponse = await getOfferAdapter(offerId)
        } else {
          offerResponse = await getOfferAdapter(offerId)
          if (offerResponse.isOk && !offerResponse.payload.isEducational) {
            return history.push(`/offre/${offerId}/individuel/edition`)
          }
        }

        loadData(offerResponse)
      }

      _loadData()
    }
  }, [
    isReady,
    offerId,
    loadData,
    history,
    enableIndividualAndCollectiveSeparation,
    isShowcase,
  ])

  return (
    <OfferEducationalLayout
      activeStep={OfferBreadcrumbStep.DETAILS}
      isCreatingOffer={false}
      offerId={offerIdFromParams}
      title="Éditer une offre"
    >
      {isReady && screenProps ? (
        <OfferEducationalScreen
          {...screenProps}
          cancelActiveBookings={cancelActiveBookings}
          initialValues={initialValues}
          isOfferActive={offer?.isActive}
          isOfferBooked={offer?.isBooked}
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
