import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from '../../../components/layout/Icon'
import { IBusinessUnitVenue } from '../BusinessUnitList'

import styles from './VenueListItem.module.scss'

interface IVenueListItemProps {
  venue: IBusinessUnitVenue
  svg: string
  hasInvalidBusinessUnit: boolean
}

const VenueListItem = ({
  venue,
  svg,
  hasInvalidBusinessUnit,
}: IVenueListItemProps): JSX.Element => (
  <div
    className={cn(styles['venue-list-item'], {
      [styles['reference-venue']]: venue.isBusinessUnitMainVenue,
    })}
  >
    <div className={styles['venue-list-item-infos']}>
      {svg && <Icon svg={svg} />}
      <span>
        {venue.publicName || venue.name} -{' '}
        {venue.siret ? (
          venue.siret
        ) : venue.isVirtual ? (
          'Offres numériques'
        ) : hasInvalidBusinessUnit ? (
          'Lieu sans SIRET'
        ) : (
          <span className={styles['venue-missing-siret']}>SIRET Manquant</span>
        )}
      </span>
    </div>
    {!venue.siret && !hasInvalidBusinessUnit && !venue.isVirtual && (
      <Link
        className={styles['venue-edit-link']}
        to={`/structures/${venue.managingOffererId}/lieux/${venue.id}?modification`}
      >
        <Icon svg="ico-outer-pen" />
        Renseigner un SIRET
      </Link>
    )}
  </div>
)

export default VenueListItem
