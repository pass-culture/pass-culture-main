import React from 'react'

import { SummaryLayout } from 'new_components/SummaryLayout'

interface ICollectiveOfferNotificationSectionProps {
  bookingEmails: string[]
}

const CollectiveOfferNotificationSection = ({
  bookingEmails,
}: ICollectiveOfferNotificationSectionProps) => {
  return (
    <SummaryLayout.SubSection title="Contact">
      {bookingEmails.map(email => (
        <SummaryLayout.Row description={email} key={email} />
      ))}
    </SummaryLayout.SubSection>
  )
}

export default CollectiveOfferNotificationSection
