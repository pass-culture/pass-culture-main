import { useCallback, useId } from 'react'

import type { GetVenuePricingPointResponseModel } from '@/apiClient/v1'
import { FormLayout } from '@/components/FormLayout/FormLayout'

import { PricingPoint } from '../PricingPoint/PricingPoint'

export interface ReimbursementFieldsProps {
  scrollToSection?: boolean
  venuePricingPoint: GetVenuePricingPointResponseModel
}
export const ReimbursementFields = ({
  scrollToSection,
  venuePricingPoint,
}: Readonly<ReimbursementFieldsProps>) => {
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
        <PricingPoint venuePricingPoint={venuePricingPoint} />
      </FormLayout.Section>
    </div>
  )
}
