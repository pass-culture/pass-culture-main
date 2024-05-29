import React from 'react'

import { GetOffererVenueResponseModel } from 'apiClient/v1'
import fullMoreIcon from 'icons/full-more.svg'
import strokeVenueIcon from 'icons/stroke-venue.svg'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './VenueItem.module.scss'

export interface VenueItemProps {
  venue: GetOffererVenueResponseModel
  offererId: number
}

export const VenueItem = ({ venue, offererId }: VenueItemProps) => {
  const { street, city, name, postalCode, publicName, id } = venue

  const showPath = `/structures/${offererId}/lieux/${id}`

  return (
    <li className={styles['venue-item']}>
      <SvgIcon alt="" src={strokeVenueIcon} className={styles['picto']} />

      <div>
        <ButtonLink
          className={styles['name']}
          link={{
            to: showPath,
            isExternal: false,
          }}
        >
          {publicName || name}
        </ButtonLink>

        <div
          className={styles['address']}
        >{`${street} ${postalCode} ${city}`}</div>
        <div>
          <ButtonLink
            className={styles['create-offer-button']}
            link={{
              to: `/offre/creation?lieu=${id}&structure=${offererId}`,
              isExternal: false,
            }}
            icon={fullMoreIcon}
          >
            {' Créer une offre'}
          </ButtonLink>
        </div>
      </div>
    </li>
  )
}
