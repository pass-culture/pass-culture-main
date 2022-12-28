import React from 'react'

import { CollectiveBookingByIdResponseModel } from 'apiClient/v1/models/CollectiveBookingByIdResponseModel'
import { InfoPhoneIcon, LocationIcon } from 'icons'
import { ReactComponent as MailIcon } from 'icons/ico-mail.svg'
import { ReactComponent as IconUser } from 'icons/ico-user.svg'

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
              <IconUser />
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
  )
}

export default CollectiveBookingDetails
