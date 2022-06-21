import {
  CollectiveOffer,
  CollectiveOfferTemplate,
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
import React, { useCallback, useEffect, useState } from 'react'
import { useHistory, useParams } from 'react-router-dom'

import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'
import OfferEducationalLayout from 'new_components/OfferEducationalLayout'
import OfferEducationalScreen from 'screens/OfferEducational'
import Spinner from 'components/layout/Spinner'
import { computeInitialValuesFromOffer } from './utils/computeInitialValuesFromOffer'
import getCollectiveOfferAdapter from 'core/OfferEducational/adapters/getCollectiveOfferAdapter'
import getCollectiveOfferTemplateAdapter from './adapters/getCollectiveOfferTemplateAdapter'
import patchCollectiveOfferAdapter from './adapters/patchCollectiveOfferAdapter'
import { patchCollectiveOfferTemplateAdapter } from './adapters/patchCollectiveOfferTemplateAdapter'
import useActiveFeature from 'components/hooks/useActiveFeature'
import useNotification from 'components/hooks/useNotification'

type AsyncScreenProps = Pick<
  IOfferEducationalProps,
  'educationalCategories' | 'educationalSubCategories' | 'userOfferers'
>

const OfferEducationalEdition = (): JSX.Element => {
  const { offerId: offerIdFromParams } = useParams<{ offerId: string }>()
  const { offerId, isShowcase } =
    extractOfferIdAndOfferTypeFromRouteParams(offerIdFromParams)
  const history = useHistory()

  const enableEducationalDomains = useActiveFeature(
    'ENABLE_EDUCATIONAL_DOMAINS'
  )
  const [isReady, setIsReady] = useState<boolean>(false)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)
  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(DEFAULT_EAC_FORM_VALUES)
  const [offer, setOffer] = useState<
    CollectiveOffer | CollectiveOfferTemplate
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
      title="Éditer une offre"
    >
      {isReady && screenProps ? (
        <OfferEducationalScreen
          {...screenProps}
          cancelActiveBookings={cancelActiveBookings}
          initialValues={initialValues}
          isOfferActive={offer?.isActive}
          isOfferBooked={offer?.isBooked}
          mode={offer?.isEditable ? Mode.EDITION : Mode.READ_ONLY}
          notify={notify}
          onSubmit={editOffer}
          setIsOfferActive={setIsOfferActive}
          getEducationalDomainsAdapter={
            enableEducationalDomains && getEducationalDomainsAdapter
          }
        />
      ) : (
        <Spinner />
      )}
    </OfferEducationalLayout>
  )
}

export default OfferEducationalEdition
