import React, { useState } from 'react'

import { GetOffererResponseModel } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import ReimbursementPoint from 'components/VenueForm/ReimbursementPoint/ReimbursementPoint'
import { Venue } from 'core/Venue/types'
import useActiveFeature from 'hooks/useActiveFeature'
import { Banner } from 'ui-kit'

import PricingPoint from '../PricingPoint'

export interface ReimbursementFieldsProps {
  offerer: GetOffererResponseModel
  venue: Venue
}

const ReimbursementFields = ({ offerer, venue }: ReimbursementFieldsProps) => {
  const isNewBankDetailsJourneyEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const venueHaveSiret = !!venue.siret
  const offererHaveVenueWithSiret = offerer.hasAvailablePricingPoints
  const [venueHasPricingPoint, setVenueHasPricingPoint] = useState<boolean>(
    !!venue.pricingPoint
  )

  return (
    <>
      <div id="reimbursement-section">
        <FormLayout.Section
          title={
            isNewBankDetailsJourneyEnabled
              ? 'Barème de remboursement'
              : 'Remboursement'
          }
        >
          {!venueHaveSiret && !offererHaveVenueWithSiret ? (
            <Banner
              links={[
                {
                  href: `/structures/${offerer.id}/lieux/creation`,
                  linkTitle: 'Créer un lieu avec SIRET',
                  isExternal: false,
                },
              ]}
            >
              Afin de pouvoir ajouter de nouvelles coordonnées bancaires, vous
              devez avoir, au minimum, un lieu rattaché à un SIRET.
            </Banner>
          ) : (
            <>
              {!venueHaveSiret && (
                <PricingPoint
                  offerer={offerer}
                  venue={venue}
                  setVenueHasPricingPoint={setVenueHasPricingPoint}
                />
              )}

              {!isNewBankDetailsJourneyEnabled && (
                <ReimbursementPoint
                  offerer={offerer}
                  initialVenue={venue}
                  venueHasPricingPoint={venueHasPricingPoint}
                />
              )}
            </>
          )}
        </FormLayout.Section>
      </div>
    </>
  )
}

export default ReimbursementFields
