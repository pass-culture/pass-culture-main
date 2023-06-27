import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'

interface CollectiveOfferNotificationSectionProps {
  bookingEmails: string[]
}

const CollectiveOfferNotificationSection = ({
  bookingEmails,
}: CollectiveOfferNotificationSectionProps) => {
  return (
    <SummaryLayout.SubSection title="Notifications des réservations">
      {bookingEmails.map(email => (
        <SummaryLayout.Row description={email} key={email} />
      ))}
    </SummaryLayout.SubSection>
  )
}

export default CollectiveOfferNotificationSection
