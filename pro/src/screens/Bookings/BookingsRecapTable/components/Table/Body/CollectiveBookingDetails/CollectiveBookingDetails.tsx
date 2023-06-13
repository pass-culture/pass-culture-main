import React from 'react'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { CollectiveBookingByIdResponseModel } from 'apiClient/v1/models/CollectiveBookingByIdResponseModel'
import PhoneIcon from 'icons/stroke-info-phone.svg'
import Icon from 'ui-kit/Icon/Icon'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import CollectiveActionButtons from '../CollectiveActionButtons'
import CollectiveTimeLine from '../CollectiveTimeLine'

import styles from './CollectiveBookingDetails.module.scss'

interface CollectiveBookingDetailsProps {
  bookingDetails: CollectiveBookingByIdResponseModel
  bookingRecap: CollectiveBookingResponseModel
  reloadBookings: () => void
}

const CollectiveBookingDetails = ({
  bookingDetails,
  bookingRecap,
  reloadBookings,
}: CollectiveBookingDetailsProps) => {
  const { educationalInstitution, educationalRedactor } = bookingDetails

  return (
    <>
      <div className={styles.container}>
        <div className={styles['details-timeline']}>
          <CollectiveTimeLine
            bookingRecap={bookingRecap}
            bookingDetails={bookingDetails}
          />
        </div>
        <div>
          <div className={styles['contact-details']}>
            <div className={styles['contact-details-title']}>
              Contact de l’établissement scolaire
            </div>
            <dl>
              <div className={styles['contact-detail']}>
                <dt className={styles['contact-detail-location-icon']}>
                  <Icon
                    className={styles['contact-detail-icon']}
                    alt="Adresse de l’établissement"
                    svg="location"
                  />
                </dt>
                <dd>
                  {`${educationalInstitution.institutionType} ${educationalInstitution.name}`.trim()}
                  <br />
                  {`${educationalInstitution.postalCode} ${educationalInstitution.city}`}
                </dd>
              </div>

              <div className={styles['contact-detail']}>
                <dt>
                  <SvgIcon
                    className={styles['contact-detail-icon']}
                    alt="Téléphone"
                    src={PhoneIcon}
                  />
                </dt>
                <dd>{educationalInstitution.phoneNumber}</dd>
              </div>

              <div className={styles['contact-detail']}>
                <dt>
                  <Icon
                    className={styles['contact-detail-icon']}
                    alt="Nom"
                    svg="ico-user"
                  />
                </dt>
                <dd>{`${educationalRedactor.firstName} ${educationalRedactor.lastName}`}</dd>
              </div>

              <div className={styles['contact-detail']}>
                <dt>
                  <Icon
                    className={styles['contact-detail-icon']}
                    alt="Email"
                    svg="ico-mail"
                  />
                </dt>
                <dd>
                  <a
                    className={styles['link-ternary']}
                    href={`mailto:${educationalRedactor.email}`}
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    {educationalRedactor.email}
                  </a>
                </dd>
              </div>
            </dl>
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
