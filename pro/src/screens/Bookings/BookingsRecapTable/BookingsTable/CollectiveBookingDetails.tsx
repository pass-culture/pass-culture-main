import React from 'react'

import { CollectiveBookingResponseModel } from 'apiClient/v1'
import { CollectiveBookingByIdResponseModel } from 'apiClient/v1/models/CollectiveBookingByIdResponseModel'
import strokeLocationIcon from 'icons/stroke-location.svg'
import strokeMailIcon from 'icons/stroke-mail.svg'
import strokePhoneIcon from 'icons/stroke-phone.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

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
                  <SvgIcon
                    className={styles['contact-detail-icon']}
                    alt="Adresse de l’établissement"
                    src={strokeLocationIcon}
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
                    src={strokePhoneIcon}
                  />
                </dt>
                <dd>{educationalInstitution.phoneNumber}</dd>
              </div>

              <div className={styles['contact-detail']}>
                <dt>
                  <SvgIcon
                    src={strokeUserIcon}
                    alt="Nom"
                    className={styles['contact-detail-icon']}
                  />
                </dt>
                <dd>{`${educationalRedactor.firstName} ${educationalRedactor.lastName}`}</dd>
              </div>

              <div className={styles['contact-detail']}>
                <dt>
                  <SvgIcon
                    className={styles['contact-detail-icon']}
                    alt="Email"
                    src={strokeMailIcon}
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
        isCancellable={bookingDetails.isCancellable}
      />
    </>
  )
}
