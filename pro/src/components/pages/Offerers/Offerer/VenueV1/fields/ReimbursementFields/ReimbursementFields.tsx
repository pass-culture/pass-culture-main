import React, { useState } from 'react'
import { IAPIOfferer } from 'core/Offerers/types'
import { IAPIVenue } from 'core/Venue/types'
import Icon from 'components/layout/Icon'
import InternalBanner from 'components/layout/InternalBanner'
import PricingPoint from '../PricingPoint/PricingPoint'

import ReimbursementPoint from '../ReimbursementPoint/ReimbursementPoint'
import styles from './ReimbursementFields.module.scss'

export interface ReimbursementInterface {
  offerer: IAPIOfferer
  readOnly: boolean
  scrollToSection?: boolean
  venue: IAPIVenue
}

const ReimbursementFields = ({
  offerer,
  readOnly,
  scrollToSection,
  venue,
}: ReimbursementInterface) => {
  const venueHaveSiret = !!venue.siret
  const offererHaveVenueWithSiret = offerer.hasAvailablePricingPoints
  const createVenuePath = `/structures/${offerer.id}/lieux/creation`
  const [venueHasPricingPoint, setVenueHasPricingPoint] = useState<boolean>(
    !!venue.pricingPoint
  )
  return (
    <>
      <div className="section">
        <h2 className="main-list-title">
          Remboursement
          <a
            className={styles['reimbursement-hint']}
            href="todo"
            rel="noopener noreferrer"
            target="_blank"
          >
            <Icon svg={'ico-external-site-filled'} />
            En savoir plus sur les remboursements
          </a>
        </h2>
        {!venueHaveSiret && !offererHaveVenueWithSiret ? (
          <InternalBanner
            href={createVenuePath}
            icon="ico-external-site-filled"
            linkTitle="Créer un lieu avec SIRET"
          >
            Afin de pouvoir ajouter de nouvelles coordonnées bancaires, vous
            devez avoir minimum un lieu rattaché à un SIRET.
          </InternalBanner>
        ) : (
          <>
            {!venueHaveSiret && (
              <PricingPoint
                readOnly={readOnly}
                offerer={offerer}
                venue={venue}
                setVenueHasPricingPoint={setVenueHasPricingPoint}
              />
            )}

            <ReimbursementPoint
              offerer={offerer}
              readOnly={readOnly}
              scrollToSection={scrollToSection}
              venue={venue}
              venueHasPricingPoint={venueHasPricingPoint}
            />
          </>
        )}
      </div>
    </>
  )
}

export default ReimbursementFields
