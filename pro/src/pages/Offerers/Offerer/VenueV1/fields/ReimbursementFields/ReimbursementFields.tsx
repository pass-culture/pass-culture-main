import React, { useCallback, useState } from 'react'

import { GetOffererResponseModel } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import ReimbursementPoint from 'components/VenueForm/ReimbursementPoint/ReimbursementPoint'
import { Venue } from 'core/Venue/types'
import useActiveFeature from 'hooks/useActiveFeature'
import { Banner } from 'ui-kit'

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
  const isNewBankDetailsJourneyEnable = useActiveFeature(
    'WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'
  )
  const venueHaveSiret = !!venue.siret
  const offererHaveVenueWithSiret = offerer.hasAvailablePricingPoints
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
        <FormLayout.Section
          title={
            isNewBankDetailsJourneyEnable
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
                  readOnly={readOnly}
                  offerer={offerer}
                  venue={venue}
                  setVenueHasPricingPoint={setVenueHasPricingPoint}
                />
              )}

              {!isNewBankDetailsJourneyEnable && (
                <ReimbursementPoint
                  offerer={offerer}
                  readOnly={readOnly}
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
