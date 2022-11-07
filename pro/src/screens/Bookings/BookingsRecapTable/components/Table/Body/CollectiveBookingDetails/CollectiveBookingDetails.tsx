import cn from 'classnames'
import React, { useState } from 'react'

import { CollectiveBookingByIdResponseModel } from 'apiClient/v1/models/CollectiveBookingByIdResponseModel'
import CancelCollectiveBookingModal from 'components/CancelCollectiveBookingModal'
import { NOTIFICATION_LONG_SHOW_DURATION } from 'core/Notification/constants'
import { cancelCollectiveBookingAdapter } from 'core/OfferEducational'
import useNotification from 'hooks/useNotification'
import { useOfferEditionURL } from 'hooks/useOfferEditionURL'
import { ReactComponent as BuildingIcon } from 'icons/building.svg'
import { ReactComponent as CalendarIcon } from 'icons/ico-calendar.svg'
import { ReactComponent as EuroIcon } from 'icons/ico-euro.svg'
import { ReactComponent as LocationIcon } from 'icons/location.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'
import { Button, ButtonLink } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { pluralizeString } from 'utils/pluralize'

import styles from './CollectiveBookingDetails.module.scss'
import {
  getLocalBeginningDatetime,
  getOfferVenue,
  getStudentsLabel,
} from './utils'

export interface ICollectiveBookingDetailsProps {
  bookingDetails: CollectiveBookingByIdResponseModel
  offerId: string
  reloadBookings: () => void
  canCancelBooking: boolean
}

const CollectiveBookingDetails = ({
  bookingDetails,
  offerId,
  reloadBookings,
  canCancelBooking,
}: ICollectiveBookingDetailsProps) => {
  const [isModalOpen, setIsModalOpen] = useState(false)

  const notify = useNotification()
  const offerEditionUrl = useOfferEditionURL(true, offerId, false, false)

  const {
    beginningDatetime,
    offerVenue,
    numberOfTickets,
    venuePostalCode,
    price,
    students,
    educationalInstitution,
    educationalRedactor,
  } = bookingDetails

  const cancelBooking = async () => {
    const response = await cancelCollectiveBookingAdapter({ offerId })
    if (response.isOk) {
      notify.success(response.message, {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
      reloadBookings()
    } else {
      notify.error(response.message, {
        duration: NOTIFICATION_LONG_SHOW_DURATION,
      })
    }
  }

  return (
    <div>
      <div className={styles['details-section']}>
        <div className={styles['details-summary-row']}>
          <div className={styles['details-summary-row-item']}>
            <CalendarIcon className={styles['details-summary-row-item-icon']} />
            {getLocalBeginningDatetime(beginningDatetime, venuePostalCode)}
          </div>
          <div className={styles['details-summary-row-item']}>
            <LocationIcon className={styles['details-summary-row-item-icon']} />
            {getOfferVenue(offerVenue)}
          </div>
        </div>
        <div className={styles['details-summary-row']}>
          <div className={styles['details-summary-row-item']}>
            <UserIcon className={styles['details-summary-row-item-icon']} />
            {`${numberOfTickets} ${pluralizeString('élève', numberOfTickets)}`}
          </div>
          <div className={styles['details-summary-row-item']}>
            <EuroIcon className={styles['details-summary-row-item-icon']} />
            {`${price}€`}
          </div>
          <div className={styles['details-summary-row-item']}>
            <BuildingIcon className={styles['details-summary-row-item-icon']} />
            {getStudentsLabel(students)}
          </div>
        </div>
      </div>

      <div className={styles['details-section']}>
        <p className={cn(styles['title'], styles['section-title'])}>
          Contact de l’établissement
        </p>
        <div>
          {`${educationalInstitution.institutionType} ${educationalInstitution.name}`.trim()}
          <br />
          {`${educationalInstitution.postalCode} ${educationalInstitution.city}`}
          <br />
          {educationalInstitution.phoneNumber}
        </div>
      </div>

      <div className={styles['details-section']}>
        <p className={cn(styles['title'], styles['section-title'])}>
          Contact de l’enseignant
        </p>
        {`${educationalRedactor.firstName} ${educationalRedactor.lastName}`}
        <br />
        {educationalRedactor.email}
      </div>

      <div className={styles['action-buttons']}>
        <Button
          variant={ButtonVariant.SECONDARY}
          onClick={() => setIsModalOpen(true)}
          disabled={!canCancelBooking}
        >
          Annuler la réservation
        </Button>
        <ButtonLink
          link={{ isExternal: false, to: offerEditionUrl }}
          variant={ButtonVariant.PRIMARY}
        >
          Éditer l’offre
        </ButtonLink>
      </div>
      {isModalOpen && (
        <CancelCollectiveBookingModal
          onDismiss={() => setIsModalOpen(false)}
          onValidate={cancelBooking}
        />
      )}
    </div>
  )
}

export default CollectiveBookingDetails
