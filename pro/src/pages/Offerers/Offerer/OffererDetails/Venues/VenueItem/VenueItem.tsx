import React from 'react'

import { GetOffererVenueResponseModel } from 'apiClient/v1'
import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import useAnalytics from 'hooks/useAnalytics'
import fullMoreIcon from 'icons/full-more.svg'
import strokeVenueIcon from 'icons/stroke-venue.svg'
import { ButtonLink } from 'ui-kit'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './VenueItem.module.scss'

export interface VenueItemProps {
  venue: GetOffererVenueResponseModel
  offererId: number
}

const VenueItem = ({ venue, offererId }: VenueItemProps) => {
  const { address, city, name, postalCode, publicName, id } = venue || {}

  const { logEvent } = useAnalytics()
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
        >{`${address} ${postalCode} ${city}`}</div>
        <div>
          <ButtonLink
            className={styles['create-offer-button']}
            link={{
              to: `/offre/creation?lieu=${id}&structure=${offererId}`,
              isExternal: false,
            }}
            onClick={() =>
              logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                from: OFFER_FORM_NAVIGATION_IN.OFFERER,
                to: OFFER_FORM_HOMEPAGE,
                used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERER_LINK,
                isEdition: false,
              })
            }
            icon={fullMoreIcon}
          >
            {' Créer une offre'}
          </ButtonLink>
        </div>
      </div>
    </li>
  )
}

export default VenueItem
