import React, { useCallback, useEffect, useState } from 'react'
import { useHistory } from 'react-router-dom'

import { NOTIFICATION_LONG_SHOW_DURATION } from 'core/Notification/constants'
import {
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
  Mode,
  cancelCollectiveBookingAdapter,
  patchIsCollectiveOfferActiveAdapter,
  patchIsTemplateOfferActiveAdapter,
  setInitialFormValues,
  CollectiveOffer,
  CollectiveOfferTemplate,
} from 'core/OfferEducational'
import getCollectiveOfferFormDataApdater from 'core/OfferEducational/adapters/getCollectiveOfferFormDataAdapter'
import patchCollectiveOfferAdapter from 'core/OfferEducational/adapters/patchCollectiveOfferAdapter'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import useNotification from 'hooks/useNotification'
import { useCollectiveOfferImageUpload } from 'pages/CollectiveOfferCreation/useCollectiveOfferImageUpload'
import OfferEducationalScreen from 'screens/OfferEducational'
import { IOfferEducationalProps } from 'screens/OfferEducational/OfferEducational'
import Spinner from 'ui-kit/Spinner/Spinner'

import { patchCollectiveOfferTemplateAdapter } from './adapters/patchCollectiveOfferTemplateAdapter'

type AsyncScreenProps = Pick<
  IOfferEducationalProps,
  'categories' | 'userOfferers' | 'domainsOptions'
>

const CollectiveOfferEdition = ({
  offer,
  reloadCollectiveOffer,
}: {
  offer: CollectiveOffer | CollectiveOfferTemplate
  reloadCollectiveOffer: () => void
}): JSX.Element => {
  const history = useHistory()

  const [isReady, setIsReady] = useState<boolean>(false)
  const [screenProps, setScreenProps] = useState<AsyncScreenProps | null>(null)
  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(DEFAULT_EAC_FORM_VALUES)

  const notify = useNotification()
  const { imageOffer, onImageDelete, onImageUpload, handleImageOnSubmit } =
    useCollectiveOfferImageUpload(offer, offer.isTemplate)

  const editOffer = useCallback(
    async (offerFormValues: IOfferEducationalFormValues) => {
      if (!offer) {
        return
      }

      const patchAdapter = offer.isTemplate
        ? patchCollectiveOfferTemplateAdapter
        : patchCollectiveOfferAdapter

      const offerResponse = await patchAdapter({
        offerId: offer.id,
        offer: offerFormValues,
        initialValues,
      })

      if (!offerResponse.isOk) {
        return notify.error(offerResponse.message)
      }
      await handleImageOnSubmit(offer.id, offer.isTemplate)

      notify.success(offerResponse.message)
      reloadCollectiveOffer()
      history.push(
        `/offre/${computeURLCollectiveOfferId(
          offer.id,
          offer.isTemplate
        )}/collectif/recapitulatif`
      )
    },
    [offer, handleImageOnSubmit]
  )

  const setIsOfferActive = async (isActive: boolean) => {
    const patchAdapter = offer.isTemplate
      ? patchIsTemplateOfferActiveAdapter
      : patchIsCollectiveOfferActiveAdapter
    const { isOk, message } = await patchAdapter({
      isActive,
      offerId: offer.id,
    })

    if (!isOk) {
      return notify.error(message)
    }

    notify.success(message)
    reloadCollectiveOffer()
  }

  const cancelActiveBookings = async () => {
    const { isOk, message } = await cancelCollectiveBookingAdapter({
      offerId: offer.id,
    })

    if (!isOk) {
      return notify.error(message, {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
    }

    notify.success(message, { duration: NOTIFICATION_LONG_SHOW_DURATION })
    reloadCollectiveOffer()
  }

  const loadData = useCallback(
    async (offerResponse: CollectiveOffer | CollectiveOfferTemplate) => {
      const offererId = offerResponse.venue.managingOffererId

      const result = await getCollectiveOfferFormDataApdater({
        offererId,
        offer: offerResponse,
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
          {
            ...values,
            ...initialValues,
          },
          offerers,
          offerers[0].id,
          offerResponse.venueId
        )
      )

      setIsReady(true)
    },
    [notify]
  )

  useEffect(() => {
    if (!isReady) {
      loadData(offer)
    }
  }, [isReady, offer.id, loadData, history, offer.isTemplate])

  if (!isReady || !screenProps || !offer) {
    return <Spinner />
  }

  return (
    <OfferEducationalScreen
      {...screenProps}
      cancelActiveBookings={cancelActiveBookings}
      initialValues={initialValues}
      isOfferActive={offer?.isActive}
      isOfferBooked={
        offer?.isTemplate ? false : offer?.collectiveStock?.isBooked
      }
      isOfferCancellable={offer && offer.isCancellable}
      mode={offer?.isEditable ? Mode.EDITION : Mode.READ_ONLY}
      onSubmit={editOffer}
      setIsOfferActive={setIsOfferActive}
      isTemplate={offer.isTemplate}
      imageOffer={imageOffer}
      onImageDelete={onImageDelete}
      onImageUpload={onImageUpload}
    />
  )
}

export default CollectiveOfferEdition
