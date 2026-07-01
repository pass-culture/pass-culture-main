import type { StudentLevels } from '@/apiClient/v1'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

interface CollectiveOfferParticipantSectionProps {
  students: StudentLevels[]
}

export const CollectiveOfferParticipantSection = ({
  students,
}: CollectiveOfferParticipantSectionProps) => {
  const isNewCollectivePriceEnabled = useActiveFeature(
    'WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS'
  )

  return (
    <SummarySubSection
      title="Participants"
      shouldShowDivider={!isNewCollectivePriceEnabled}
    >
      <SummaryDescriptionList
        descriptions={students.map((student) => ({ text: student }))}
      />
    </SummarySubSection>
  )
}
