import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

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
