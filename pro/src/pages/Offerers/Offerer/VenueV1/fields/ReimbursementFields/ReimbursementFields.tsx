import React, { useCallback } from 'react'

import { GetOffererResponseModel, GetVenueResponseModel } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { Banner } from 'ui-kit'

import PricingPoint from '../PricingPoint'

export interface ReimbursementFieldsProps {
  offerer: GetOffererResponseModel
  scrollToSection?: boolean
  venue: GetVenueResponseModel
}

const ReimbursementFields = ({
  offerer,
  scrollToSection,
  venue,
}: ReimbursementFieldsProps) => {
  const venueHaveSiret = !!venue.siret
  const offererHaveVenueWithSiret = offerer.hasAvailablePricingPoints

  const scrollToReimbursementSection = useCallback((node: any) => {
    if (node !== null && scrollToSection) {
      setTimeout(() => {
        node.scrollIntoView()
      }, 200)
    }
  }, [])

  return (
    <>
      <div ref={scrollToReimbursementSection} id="reimbursement-section">
        <FormLayout.Section title="Barème de remboursement">
          {!venueHaveSiret && !offererHaveVenueWithSiret ? (
            <Banner
              links={[
                {
                  href: `/structures/${offerer.id}/lieux/creation`,
                  label: 'Créer un lieu avec SIRET',
                },
              ]}
            >
              Afin de pouvoir ajouter de nouvelles coordonnées bancaires, vous
              devez avoir, au minimum, un lieu rattaché à un SIRET.
            </Banner>
          ) : (
            <>
              {!venueHaveSiret && (
                <PricingPoint offerer={offerer} venue={venue} />
              )}
            </>
          )}
        </FormLayout.Section>
      </div>
    </>
  )
}

export default ReimbursementFields
