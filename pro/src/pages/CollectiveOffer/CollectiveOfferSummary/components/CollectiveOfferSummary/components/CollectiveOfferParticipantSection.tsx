import { StudentLevels } from '@/apiClient//v1'
import { SummaryDescriptionList } from '@/components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from '@/components/SummaryLayout/SummarySubSection'

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
