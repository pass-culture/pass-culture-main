import React from 'react'

import { NOTIFICATION_LONG_SHOW_DURATION } from 'core/Notification/constants'
import {
  Mode,
  cancelCollectiveBookingAdapter,
  patchIsCollectiveOfferActiveAdapter,
  patchIsTemplateOfferActiveAdapter,
  CollectiveOffer,
  CollectiveOfferTemplate,
} from 'core/OfferEducational'
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
