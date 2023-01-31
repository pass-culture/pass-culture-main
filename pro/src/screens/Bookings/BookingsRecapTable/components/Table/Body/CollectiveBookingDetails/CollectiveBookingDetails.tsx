import React from 'react'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { CollectiveBookingByIdResponseModel } from 'apiClient/v1/models/CollectiveBookingByIdResponseModel'
import { InfoPhoneIcon, LocationIcon, MailIcon, User2Icon } from 'icons'

import CollectiveActionButtons from '../CollectiveActionButtons'
import CollectiveTimeLine from '../CollectiveTimeLine'

import styles from './CollectiveBookingDetails.module.scss'

export interface ICollectiveBookingDetailsProps {
  bookingDetails: CollectiveBookingByIdResponseModel
  bookingRecap: CollectiveBookingResponseModel
  reloadBookings: () => void
}

const CollectiveBookingDetails = ({
  bookingDetails,
  bookingRecap,
  reloadBookings,
}: ICollectiveBookingDetailsProps) => {
  const { educationalInstitution, educationalRedactor } = bookingDetails

  return (
    <>
      <div className={styles.container}>
        <div className={styles['details-column']}>
          <CollectiveTimeLine
            bookingRecap={bookingRecap}
            bookingDetails={bookingDetails}
          />
        </div>
        <div className={styles['details-column']}>
          <div className={styles['contact-details']}>
            <div className={styles['contact-details-title']}>
              Contact de l’établissement scolaire
            </div>

            <div className={styles['contact-detail']}>
              <div className={styles['contact-detail-icon']}>
                <LocationIcon />
              </div>
              {`${educationalInstitution.institutionType} ${educationalInstitution.name}`.trim()}
            </div>

            <div className={styles['contact-detail']}>
              <div className={styles['contact-detail-icon']}>
                <InfoPhoneIcon />
              </div>
              {educationalInstitution.phoneNumber}
            </div>

            <div className={styles['contact-detail']}>
              <div className={styles['contact-detail-icon']}>
                <User2Icon />
              </div>
              {`${educationalRedactor.firstName} ${educationalRedactor.lastName}`}
            </div>

            <div className={styles['contact-detail']}>
              <div className={styles['contact-detail-icon']}>
                <MailIcon />
              </div>
              <a
                className={styles['link-ternary']}
                href={`mailto:${educationalRedactor.email}`}
                rel="noopener noreferrer"
                target="_blank"
              >
                {educationalRedactor.email}
              </a>
            </div>
          </div>
        </div>
      </div>
      <CollectiveActionButtons
        bookingRecap={bookingRecap}
        reloadBookings={reloadBookings}
        isCancellable={bookingDetails.isCancellable}
      />
    </>
  )
}

export default CollectiveBookingDetails
