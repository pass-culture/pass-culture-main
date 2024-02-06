import React from 'react'

import { SummaryRow } from 'components/SummaryLayout/SummaryRow'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

interface CollectiveOfferNotificationSectionProps {
  bookingEmails: string[]
}

const CollectiveOfferNotificationSection = ({
  bookingEmails,
}: CollectiveOfferNotificationSectionProps) => {
  return (
    <SummarySubSection title="Notifications des réservations">
      {bookingEmails.map((email) => (
        <SummaryRow description={email} key={email} />
      ))}
    </SummarySubSection>
  )
}

export default CollectiveOfferNotificationSection
