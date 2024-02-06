import React from 'react'

import { SummaryRow } from 'components/SummaryLayout/SummaryRow'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

interface CollectiveOfferContactSectionProps {
  phone?: string | null
  email: string
}

const CollectiveOfferContactSection = ({
  phone,
  email,
}: CollectiveOfferContactSectionProps) => {
  return (
    <SummarySubSection title="Contact">
      <SummaryRow title="Téléphone" description={phone} />
      <SummaryRow title="Email" description={email} />
    </SummarySubSection>
  )
}

export default CollectiveOfferContactSection
