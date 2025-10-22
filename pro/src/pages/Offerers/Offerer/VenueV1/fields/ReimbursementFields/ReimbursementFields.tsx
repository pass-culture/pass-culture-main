import { useCallback, useId } from 'react'

import type {
  GetOffererResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Callout } from '@/ui-kit/Callout/Callout'

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
  const offererHaveVenueWithSiret = offerer.hasAvailablePricingPoints
  const reimbursementSection = useId()

  const scrollToReimbursementSection = useCallback(
    (node: { scrollIntoView: () => void } | null) => {
      if (node !== null && scrollToSection) {
        setTimeout(() => {
          node.scrollIntoView()
        }, 200)
      }
    },
    [scrollToSection]
  )

  return (
    <div ref={scrollToReimbursementSection} id={reimbursementSection}>
      <FormLayout.Section title="Barème de remboursement">
        {!venue.siret && !offererHaveVenueWithSiret ? (
          <Callout
            links={[
              {
                href: `/inscription/structure/recherche`,
                label: 'Créer une structure avec SIRET',
              },
            ]}
          >
            Afin de pouvoir ajouter de nouvelles coordonnées bancaires, vous
            devez avoir, au minimum, une structure rattachée à un SIRET.
          </Callout>
        ) : (
          <PricingPoint offerer={offerer} venue={venue} />
        )}
      </FormLayout.Section>
    </div>
  )
}
