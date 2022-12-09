import React from 'react'

import { CollectiveBookingByIdResponseModel } from 'apiClient/v1/models/CollectiveBookingByIdResponseModel'
import { ReactComponent as GeolocIcon } from 'icons/ico-geoloc-solid.svg'
import { ReactComponent as MailIcon } from 'icons/ico-mail.svg'
import { ReactComponent as PhoneIcon } from 'icons/ico-phone.svg'
import { ReactComponent as UserIcon } from 'icons/ico-user-solid.svg'

import styles from './CollectiveBookingDetails.module.scss'

export interface ICollectiveBookingDetailsProps {
  bookingDetails: CollectiveBookingByIdResponseModel
}

const CollectiveBookingDetails = ({
  bookingDetails,
}: ICollectiveBookingDetailsProps) => {
  const { educationalInstitution, educationalRedactor } = bookingDetails

  return (
    <div className={styles.container}>
      <div className={styles['details-column']}>La timeline sera ici</div>
      <div className={styles['details-column']}>
        <div className={styles['contact-details']}>
          <div className={styles['contact-details-title']}>
            Contact de l’établissement scolaire
          </div>

          <div className={styles['contact-detail']}>
            <GeolocIcon className={styles['contact-detail-icon']} />
            {`${educationalInstitution.institutionType} ${educationalInstitution.name}`.trim()}
          </div>

          <div className={styles['contact-detail']}>
            <PhoneIcon className={styles['contact-detail-icon']} />
            {educationalInstitution.phoneNumber}
          </div>

          <div className={styles['contact-detail']}>
            <UserIcon className={styles['contact-detail-icon']} />
            {`${educationalRedactor.firstName} ${educationalRedactor.lastName}`}
          </div>

          <div className={styles['contact-detail']}>
            <MailIcon className={styles['contact-detail-icon']} />
            {educationalRedactor.email}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CollectiveBookingDetails
