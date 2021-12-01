import React from 'react'

import Icon from 'components/layout/Icon'

import BusinessUnitForm from '../BusinessUnitForm'
import { IBusinessUnit, IBusinessUnitVenue } from '../BusinessUnitList'
import VenueListItem from '../VenueListItem/VenueListItem'

import styles from './BusinessUnitCard.module.scss'

interface IBusinessUnitCardProps {
  className?: string
  businessUnit: IBusinessUnit
  saveBusinessUnit: (businessUnitId: number, siret: string) => void
  venues: IBusinessUnitVenue[]
}

const BusinessUnitCard = ({
  className = '',
  businessUnit,
  saveBusinessUnit,
  venues,
}: IBusinessUnitCardProps): JSX.Element => {
  const nbVenues = venues.length
  const computeVenueIcon = (venue: IBusinessUnitVenue) => {
    if (venue.isVirtual) return ''
    if (businessUnit.siret) {
      return venue.isBusinessUnitMainVenue ? 'ico-validate-purple' : ''
    }
    return venue.siret ? 'ico-validate-green' : 'ico-clear-red'
  }

  return (
    <div
      className={`${styles['business-unit-card']} ${className}`}
      key={businessUnit.id}
    >
      <h3 className={styles['business-unit-title']}>
        {!businessUnit.siret && <Icon svg="ico-alert-filled" />}
        {businessUnit.name}
      </h3>
      <div className={styles['business-unit-informations']}>
        <ul className={styles['business-unit-bank-informations']}>
          <li key="iban">
            <span className={styles['bank-information-label']}>IBAN : </span>
            <span>{businessUnit.iban}</span>
          </li>
          <li key="bic">
            <span className={styles['bank-information-label']}>BIC : </span>
            <span>{businessUnit.bic}</span>
          </li>
        </ul>
        {businessUnit.siret && (
          <div className={styles['business-unit-reference-siret']}>
            <div className={styles['business-unit-siret-label']}>
              SIRET de référence du point de remboursement :
            </div>
            {businessUnit.siret}
          </div>
        )}
      </div>

      <div className={styles['venue-list']}>
        <h4>
          {nbVenues > 1
            ? `${nbVenues} lieux utilisent ce point de remboursement :`
            : `${nbVenues} lieu utilise ce point de remboursement :`}
        </h4>
        {venues.map(
          (venue: IBusinessUnitVenue): JSX.Element => (
            <VenueListItem
              hasInvalidBusinessUnit={!!businessUnit.siret}
              key={venue.id}
              svg={computeVenueIcon(venue)}
              venue={venue}
            />
          )
        )}

        {!businessUnit.siret && venues.some(venue => venue.siret) && (
          <>
            <h4 className={styles['reference-siret-title']}>
              SIRET de référence
            </h4>
            <span>
              Ce SIRET figurera sur les justificatifs comptables des lieux
              rattachés à ce point de remboursement.
            </span>
            <BusinessUnitForm
              businessUnit={businessUnit}
              className={styles['business-unit-form']}
              onSubmit={saveBusinessUnit}
              venues={venues}
            />
          </>
        )}
      </div>
    </div>
  )
}

export default BusinessUnitCard
