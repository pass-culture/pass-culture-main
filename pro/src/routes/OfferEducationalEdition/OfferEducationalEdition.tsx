import React, { useCallback, useEffect, useState } from 'react'
import { useHistory, useParams } from 'react-router-dom'

import {
  GetCollectiveOfferResponseModel,
  GetCollectiveOfferTemplateResponseModel,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import useNotification from 'components/hooks/useNotification'
import Spinner from 'components/layout/Spinner'
import {
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  Mode,
  cancelCollectiveBookingAdapter,
  extractOfferIdAndOfferTypeFromRouteParams,
  getCategoriesAdapter,
  getEducationalDomainsAdapter,
  getOfferersAdapter,
  patchIsCollectiveOfferActiveAdapter,
  patchIsTemplateOfferActiveAdapter,
  setInitialFormValues,
} from 'core/OfferEducational'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import OfferEducationalScreen from 'screens/OfferEducational'
import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'

import getCollectiveOfferTemplateAdapter from './adapters/getCollectiveOfferTemplateAdapter'
import patchCollectiveOfferAdapter from './adapters/patchCollectiveOfferAdapter'
import { patchCollectiveOfferTemplateAdapter } from './adapters/patchCollectiveOfferTemplateAdapter'
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

  const [isReady, setIsReady] = useState<boolean>(false)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)
  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(DEFAULT_EAC_FORM_VALUES)
  const [offer, setOffer] = useState<
    GetCollectiveOfferResponseModel | GetCollectiveOfferTemplateResponseModel
  >()
  const notify = useNotification()

  const editOffer = useCallback(
    async (offerFormValues: IOfferEducationalFormValues) => {
      if (offer) {
        const patchAdapter = isShowcase
          ? patchCollectiveOfferTemplateAdapter
          : patchCollectiveOfferAdapter
        const offerResponse = await patchAdapter({
          offerId,
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
    const patchAdapter = isShowcase
      ? patchIsTemplateOfferActiveAdapter
      : patchIsCollectiveOfferActiveAdapter
    const { isOk, message } = await patchAdapter({
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
    const { isOk, message } = await cancelCollectiveBookingAdapter({
      offerId,
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
        | AdapterSuccess<GetCollectiveOfferResponseModel>
        | AdapterSuccess<GetCollectiveOfferTemplateResponseModel>
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
        (offerSubcategory?.id ??
          DEFAULT_EAC_FORM_VALUES.subCategory) as SubcategoryIdEnum
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
        const getOfferAdapter = isShowcase
          ? getCollectiveOfferTemplateAdapter
          : getCollectiveOfferAdapter
        const offerResponse = await getOfferAdapter(offerId)

        loadData(offerResponse)
      }

      _loadData()
    }
  }, [isReady, offerId, loadData, history, isShowcase])

  return (
    <OfferEducationalLayout
      activeStep={OfferBreadcrumbStep.DETAILS}
      isCreatingOffer={false}
      offerId={offerIdFromParams}
      title="Éditer une offre collective"
    >
      {isReady && screenProps ? (
        <OfferEducationalScreen
          {...screenProps}
          cancelActiveBookings={cancelActiveBookings}
          initialValues={initialValues}
          isOfferActive={offer?.isActive}
          isOfferBooked={
            offer && 'collectiveStock' in offer
              ? offer?.collectiveStock?.isBooked
              : false
          }
          isOfferCancellable={offer && offer.isCancellable}
          mode={offer?.isEditable ? Mode.EDITION : Mode.READ_ONLY}
          notify={notify}
          onSubmit={editOffer}
          setIsOfferActive={setIsOfferActive}
          getEducationalDomainsAdapter={getEducationalDomainsAdapter}
        />
      ) : (
        <Spinner />
      )}
    </OfferEducationalLayout>
  )
}

export default OfferEducationalEdition
