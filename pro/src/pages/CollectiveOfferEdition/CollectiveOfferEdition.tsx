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
import useNotification from 'hooks/useNotification'
import OfferEducationalScreen from 'screens/OfferEducational'
import useOfferEducationalFormData from 'screens/OfferEducational/useOfferEducationalFormData'
import Spinner from 'ui-kit/Spinner/Spinner'

const CollectiveOfferEdition = ({
  offer,
  reloadCollectiveOffer,
  setOffer,
}: {
  offer: CollectiveOffer | CollectiveOfferTemplate
  reloadCollectiveOffer: () => void
  setOffer: (offer: CollectiveOffer | CollectiveOfferTemplate) => void
}): JSX.Element => {
  const history = useHistory()

  const [initialValues, setInitialValues] =
    useState<IOfferEducationalFormValues>(DEFAULT_EAC_FORM_VALUES)

  const notify = useNotification()
  const { isReady, ...offerEducationalFormData } = useOfferEducationalFormData(
    offer.venue.managingOffererId,
    offer
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

      const { offerers, initialValues } = result.payload

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
    },
    [notify]
  )

  useEffect(() => {
    if (!isReady) {
      loadData(offer)
    }
  }, [isReady, offer.id, loadData, history, offer.isTemplate])

  if (!isReady || !offer) {
    return <Spinner />
  }

  return (
    <OfferEducationalScreen
      categories={offerEducationalFormData.categories}
      userOfferers={offerEducationalFormData.offerers}
      domainsOptions={offerEducationalFormData.domains}
      offer={offer}
      setOffer={setOffer}
      cancelActiveBookings={cancelActiveBookings}
      initialValues={initialValues}
      isOfferActive={offer?.isActive}
      isOfferBooked={
        offer?.isTemplate ? false : offer?.collectiveStock?.isBooked
      }
      isOfferCancellable={offer && offer.isCancellable}
      mode={offer?.isEditable ? Mode.EDITION : Mode.READ_ONLY}
      setIsOfferActive={setIsOfferActive}
      isTemplate={offer.isTemplate}
    />
  )
}

export default CollectiveOfferEdition
