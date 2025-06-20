import useSWR from 'swr'

import { api } from 'apiClient/api'
import {
  CollectiveBookingResponseModel,
  CollectiveOfferAllowedAction,
} from 'apiClient/v1'
import { CollectiveBookingByIdResponseModel } from 'apiClient/v1/models/CollectiveBookingByIdResponseModel'
import { GET_COLLECTIVE_OFFER_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { isActionAllowedOnCollectiveOffer } from 'commons/utils/isActionAllowedOnCollectiveOffer'
import { EducationalInstitutionDetails } from 'components/EducationalInstitutionDetails/EducationalInstititutionDetails'

import { CollectiveActionButtons } from './CollectiveActionButtons'
import styles from './CollectiveBookingDetails.module.scss'
import { CollectiveTimeLine } from './CollectiveTimeLine'

interface CollectiveBookingDetailsProps {
  bookingDetails: CollectiveBookingByIdResponseModel
  bookingRecap: CollectiveBookingResponseModel
}

export const CollectiveBookingDetails = ({
  bookingDetails,
  bookingRecap,
}: CollectiveBookingDetailsProps) => {
  const { data: offer } = useSWR(
    [GET_COLLECTIVE_OFFER_QUERY_KEY, Number(bookingRecap.stock.offerId)],
    ([, offerIdParam]) => api.getCollectiveOffer(offerIdParam)
  )

  const bookingIsCancellable =
    offer &&
    isActionAllowedOnCollectiveOffer(
      offer,
      CollectiveOfferAllowedAction.CAN_CANCEL
    )

  const bookingCanEditDiscount =
    offer &&
    isActionAllowedOnCollectiveOffer(
      offer,
      CollectiveOfferAllowedAction.CAN_EDIT_DISCOUNT
    )

  const { educationalInstitution, educationalRedactor } = bookingDetails

  return (
    <>
      <div className={styles.container}>
        <div className={styles['details-timeline']}>
          <CollectiveTimeLine
            bookingRecap={bookingRecap}
            canEditDiscount={bookingCanEditDiscount || false}
            bookingDetails={bookingDetails}
          />
        </div>
        <EducationalInstitutionDetails educationalInstitution={educationalInstitution} educationalRedactor={educationalRedactor} />
      </div>

      <CollectiveActionButtons
        bookingRecap={bookingRecap}
        isCancellable={bookingIsCancellable || false}
      />
    </>
  )
}

