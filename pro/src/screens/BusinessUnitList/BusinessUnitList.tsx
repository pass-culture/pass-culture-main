import React from 'react'
import { NavLink } from 'react-router-dom'

import Divider from 'ui-kit/Divider'
import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'

import BusinessUnitCard from './BusinessUnitCard'
import styles from './BusinessUnitList.module.scss'

export interface IBusinessUnitVenue {
  id: string
  name: string
  siret: string | null
  businessUnitId: number | null
  managingOffererId: string
}

export interface IBusinessUnit {
  id: number
  name: string
  bic: string
  iban: string
  siret: string | null
}

export interface IOfferer {
  id: string
  name: string
}

interface IBusinessUnitListProps {
  offerer: IOfferer
  businessUnitList: IBusinessUnit[]
  saveBusinessUnit: () => void,
  venues: IBusinessUnitVenue[],
}

const BusinessUnitList = ({
  offerer,
  businessUnitList,
  saveBusinessUnit,
  venues,
}: IBusinessUnitListProps): JSX.Element => {

  const getBusinessUnitVenues = (businessUnit: IBusinessUnit): IBusinessUnitVenue[] => venues.filter(
    (venue:IBusinessUnitVenue) => venue.businessUnitId === businessUnit.id
  )

  return (
    <div className={styles['business-unit-page']}>
      <NavLink
        className="back-button has-text-primary"
        to={`/accueil?structure=${offerer.id}`}
      >
        <Icon svg="ico-back" />
        Accueil
      </NavLink>
      <PageTitle title="Points de facturations" />
      <Titles subtitle={`Structure : ${offerer.name}`} title="Points de facturations" />

      <p className={styles['description']}>
        TODO expliquer ce que sont les points de facturation!
      </p>

      <Divider/>
      <div>
        <div className={styles['business-unit-list-section']}>
          <h4>Points de facturations invalides</h4>
          <p className={styles['description']}>
            Les points de facturation ci-dessous ne sont seront plus valide au 1er janvier 2022. Afin de continuer à percevoir vos remboursement vous devez indiquer un siret de reference.
          </p>

          {businessUnitList.filter((businessUnit) => !businessUnit.siret).map((bu: IBusinessUnit) => (
            <BusinessUnitCard
              businessUnit={bu}
              className={styles['business-unit-list-item']}
              key={bu.id}
              saveBusinessUnit={saveBusinessUnit}
              venues={getBusinessUnitVenues(bu)}
            />
          ))}
        </div>

        <div className={styles['business-unit-list-section']}>
          <h4>Points de facturations</h4>
          <p className={styles['description']}>
            Ci-dessous les point de facturation valide utilisées par votre structure.
          </p>
          {businessUnitList.filter((businessUnit) => businessUnit.siret).map((bu: IBusinessUnit) => (
            <BusinessUnitCard
              businessUnit={bu}
              className={styles['business-unit-list-item']}
              key={bu.id}
              saveBusinessUnit={saveBusinessUnit}
              venues={getBusinessUnitVenues(bu)}
            />
          ))}
        </div>
      </div>
    </div>
  )
}

export default BusinessUnitList
