import React from 'react'

import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

interface CollectiveOfferNotificationSectionProps {
  bookingEmails: string[]
}

export const CollectiveOfferNotificationSection = ({
  bookingEmails,
}: CollectiveOfferNotificationSectionProps) => {
  return (
    <SummarySubSection
      title="Notifications des réservations"
      shouldShowDivider={false}
    >
      <SummaryDescriptionList
        descriptions={bookingEmails.map((email) => ({ text: email }))}
      />
    </SummarySubSection>
  )
}
