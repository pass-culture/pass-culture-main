import type { StudentLevels } from '@/apiClient/v1'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/ui-kit/SummaryLayout/SummarySubSection'

interface CollectiveOfferParticipantSectionProps {
  students: StudentLevels[]
}

export const CollectiveOfferParticipantSection = ({
  students,
}: CollectiveOfferParticipantSectionProps) => {
  return (
    <SummarySubSection title="Participants">
      <SummaryDescriptionList
        descriptions={students.map((student) => ({ text: student }))}
      />
    </SummarySubSection>
  )
}
