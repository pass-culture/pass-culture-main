import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'

interface ICollectiveOfferContactSectionProps {
  phone: string
  email: string
}

const CollectiveOfferContactSection = ({
  phone,
  email,
}: ICollectiveOfferContactSectionProps) => {
  return (
    <SummaryLayout.SubSection title="Contact">
      <SummaryLayout.Row title="Téléphone" description={phone} />
      <SummaryLayout.Row title="E-mail" description={email} />
    </SummaryLayout.SubSection>
  )
}

export default CollectiveOfferContactSection
