import cn from 'classnames'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import Card from 'ui-kit/Card'
import DescriptionList from 'ui-kit/DescriptionList'
import IListItem from 'ui-kit/DescriptionList/DescriptionList'

import BusinessUnitForm from '../BusinessUnitForm'
import { IBusinessUnit, IBusinessUnitVenue } from '../BusinessUnitList'

import styles from './BusinessUnitCard.module.scss'

interface IBusinessUnitCardProps {
  className?: string
  businessUnit: IBusinessUnit
  saveBusinessUnit: () => void
  venues: IBusinessUnitVenue[]
}

const BusinessUnitCard = ({
  className = '',
  businessUnit,
  saveBusinessUnit,
  venues,
}: IBusinessUnitCardProps) => {
  const nbVenues = venues.length
  let businessUnitInformations = [
    { label: 'BIC', value: businessUnit.bic },
    { label: 'IBAN', value: businessUnit.iban },
  ]

  if (businessUnit.siret) {
    businessUnitInformations = [
      { label: 'SIRET', value: businessUnit.siret },
      ...businessUnitInformations
    ]
  }

  return (
    <Card cardStyle={businessUnit.siret ? 'secondary' : 'primary'} className={className} key={businessUnit.id} title={businessUnit.name}>
      <>
        { !businessUnit.siret && (
          <BusinessUnitForm
            className={styles['business-unit-form']}
            businessUnit={businessUnit}
            venues={venues}
            onSubmit={saveBusinessUnit}
          />
        )}

        <DescriptionList list={businessUnitInformations}/>

        <div className={styles['venue-list']}>
          <h4>
            { nbVenues > 1 ?
              `${nbVenues} lieux utilisent ce point de facturation.`
            :
              `${nbVenues} lieu utilise ce point de facturation.`
            }
          </h4>
          {venues.map(
            (venue: IBusinessUnitVenue): JSX.Element => (
              <div className={styles['venue-list-item']} key={venue.id}>
                {`${venue.name} - ${venue.siret ? venue.siret : 'SIRET non renseigné'}`}
                <Link className={cn(styles['venue-edit-link'], 'tertiary-link')} to={`/structures/${venue.managingOffererId}/lieux/${venue.id}`}>
                  Voir
                </Link>
              </div>
            )
          )}
        </div>

      </>
    </Card>
  )
}

export default BusinessUnitCard
