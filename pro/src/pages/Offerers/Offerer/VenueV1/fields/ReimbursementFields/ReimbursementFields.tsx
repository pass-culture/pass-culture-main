import { useCallback, useId } from 'react'

import type {
  GetOffererResponseModel,
  GetVenueResponseModel,
} from '@/apiClient/v1'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Banner } from '@/design-system/Banner/Banner'
import fullNextIcon from '@/icons/full-next.svg'

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
          <Banner
            title="Structure SIRET nécessaire"
            actions={[
              {
                href: `/inscription/structure/recherche`,
                label: 'Créer une structure avec SIRET',
                icon: fullNextIcon,
                type: 'link',
              },
            ]}
            description="L'ajout de coordonnées bancaires nécessite au moins une structure rattachée à un SIRET."
          />
        ) : (
          <PricingPoint offerer={offerer} venue={venue} />
        )}
      </FormLayout.Section>
    </div>
  )
}
