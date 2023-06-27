import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'

interface CollectiveOfferContactSectionProps {
  phone?: string | null
  email: string
}

const CollectiveOfferContactSection = ({
  phone,
  email,
}: CollectiveOfferContactSectionProps) => {
  return (
    <SummaryLayout.SubSection title="Contact">
      <SummaryLayout.Row title="Téléphone" description={phone} />
      <SummaryLayout.Row title="Email" description={email} />
    </SummaryLayout.SubSection>
  )
}

export default CollectiveOfferContactSection
