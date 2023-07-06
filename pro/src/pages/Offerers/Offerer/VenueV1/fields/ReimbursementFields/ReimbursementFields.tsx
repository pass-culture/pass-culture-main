import React, { useCallback, useState } from 'react'

import { GetOffererResponseModel } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import ReimbursementPoint from 'components/VenueForm/ReimbursementPoint/ReimbursementPoint'
import { Venue } from 'core/Venue'
import { ReactComponent as FullLink } from 'icons/full-link.svg'
import InternalBanner from 'ui-kit/Banners/InternalBanner'

import PricingPoint from '../PricingPoint'

export interface ReimbursementFieldsProps {
  offerer: GetOffererResponseModel
  readOnly: boolean
  scrollToSection?: boolean
  venue: Venue
}

const ReimbursementFields = ({
  offerer,
  readOnly,
  scrollToSection,
  venue,
}: ReimbursementFieldsProps) => {
  const venueHaveSiret = !!venue.siret
  const offererHaveVenueWithSiret = offerer.hasAvailablePricingPoints
  const createVenuePath = `/structures/${offerer.id}/lieux/creation`
  const [venueHasPricingPoint, setVenueHasPricingPoint] = useState<boolean>(
    !!venue.pricingPoint
  )

  const scrollToReimbursementSection = useCallback((node: any) => {
    if (scrollToSection) {
      setTimeout(() => {
        node.scrollIntoView()
      }, 200)
    }
  }, [])

  return (
    <>
      <div ref={scrollToReimbursementSection} id="reimbursement-section">
        <FormLayout.Section title="Remboursement">
          {!venueHaveSiret && !offererHaveVenueWithSiret ? (
            <InternalBanner
              to={createVenuePath}
              Icon={FullLink}
              linkTitle="Créer un lieu avec SIRET"
            >
              Afin de pouvoir ajouter de nouvelles coordonnées bancaires, vous
              devez avoir, au minimum, un lieu rattaché à un SIRET.
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
                initialVenue={venue}
                venueHasPricingPoint={venueHasPricingPoint}
              />
            </>
          )}
        </FormLayout.Section>
      </div>
    </>
  )
}

export default ReimbursementFields
