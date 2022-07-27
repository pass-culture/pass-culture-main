import React from 'react'

import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'
import { Banner } from 'ui-kit'

import BusinessUnitCard from './BusinessUnitCard'
import styles from './BusinessUnitList.module.scss'

export interface IBusinessUnitVenue {
  id: string
  name: string
  publicName: string
  siret: string | null
  businessUnitId: number | null
  managingOffererId: string
  isBusinessUnitMainVenue: boolean | null
  isVirtual: boolean
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
  hasDigitalVenueAtLeastOneOffer: boolean
}

interface IBusinessUnitListProps {
  offerer: IOfferer
  businessUnitList: IBusinessUnit[]
  saveBusinessUnit: (businessUnitId: number, siret: string) => void
  venues: IBusinessUnitVenue[]
}

const BusinessUnitList = ({
  offerer,
  businessUnitList,
  saveBusinessUnit,
  venues,
}: IBusinessUnitListProps): JSX.Element => {
  const getBusinessUnitVenues = (
    businessUnit: IBusinessUnit
  ): IBusinessUnitVenue[] => {
    let filteredVenues = venues
    if (!offerer.hasDigitalVenueAtLeastOneOffer) {
      filteredVenues = venues.filter(
        (venue: IBusinessUnitVenue) => !venue.isVirtual
      )
    }
    return filteredVenues.filter(
      (venue: IBusinessUnitVenue) => venue.businessUnitId === businessUnit.id
    )
  }
  const invalidBusinessUnits = businessUnitList.filter(
    businessUnit => !businessUnit.siret
  )
  const validBusinessUnits = businessUnitList.filter(
    businessUnit => businessUnit.siret
  )

  return (
    <div className={styles['business-unit-page']}>
      <PageTitle title="Points de remboursement" />
      <Titles subtitle={offerer.name} title="Points de remboursement" />

      <Banner
        className={styles['business-unit-info-banner']}
        href="https://aide.passculture.app/hc/fr/articles/4413973462929--Acteurs-Culturels-Comment-rattacher-mes-points-de-remboursement-et-mes-coordonn%C3%A9es-bancaires-%C3%A0-un-SIRET-de-r%C3%A9f%C3%A9rence-"
        linkTitle="En savoir plus sur les points de remboursements"
        type="notification-info"
      >
        À partir de janvier 2022, vous recevrez un justificatif et un virement
        unique pour les lieux d’un même point de remboursement. Pour chaque
        point de remboursement, il vous faut renseigner un SIRET de référence
        qui figurera sur vos justificatifs.
      </Banner>

      <div>
        {invalidBusinessUnits.length > 0 && (
          <div className={styles['business-unit-list-section']}>
            <h3>Points de remboursement invalides</h3>
            <p className={styles['description']}>
              Les points de remboursement suivants ne seront plus valides à
              partir de janvier 2022. Pour continuer à percevoir vos
              remboursements vous devez renseigner un SIRET de référence pour
              chacun d’entre eux.
            </p>

            {invalidBusinessUnits.map((bu: IBusinessUnit) => (
              <BusinessUnitCard
                businessUnit={bu}
                className={styles['business-unit-list-item']}
                key={bu.id}
                saveBusinessUnit={saveBusinessUnit}
                venues={getBusinessUnitVenues(bu)}
              />
            ))}
          </div>
        )}

        {validBusinessUnits.length > 0 && (
          <div className={styles['business-unit-list-section']}>
            <h3>Points de remboursement valides</h3>
            <p className={styles['description']}>
              Ci-dessous les points de remboursement valides utilisés par votre
              structure.
            </p>
            {validBusinessUnits.map((bu: IBusinessUnit) => (
              <BusinessUnitCard
                businessUnit={bu}
                className={styles['business-unit-list-item']}
                key={bu.id}
                saveBusinessUnit={saveBusinessUnit}
                venues={getBusinessUnitVenues(bu)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default BusinessUnitList
