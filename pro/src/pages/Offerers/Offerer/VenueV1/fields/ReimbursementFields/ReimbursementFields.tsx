import { useCallback } from 'react'

import { GetOffererResponseModel, GetVenueResponseModel } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { Callout } from 'ui-kit/Callout/Callout'

import { PricingPoint } from '../PricingPoint/PricingPoint'

export interface ReimbursementFieldsProps {
  offerer: GetOffererResponseModel
  scrollToSection?: boolean
  venue: GetVenueResponseModel
}

export const ReimbursementFields = ({
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
            <Callout
              links={[
                {
                  href: `/parcours-inscription/structure`,
                  label: 'Créer une structure avec SIRET',
                },
              ]}
            >
              Afin de pouvoir ajouter de nouvelles coordonnées bancaires, vous
              devez avoir, au minimum, une structure rattachée à un SIRET.
            </Callout>
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
