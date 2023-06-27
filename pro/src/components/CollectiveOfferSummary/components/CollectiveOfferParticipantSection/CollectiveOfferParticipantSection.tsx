import React from 'react'

import { StudentLevels } from 'apiClient/v1'
import { SummaryLayout } from 'components/SummaryLayout'

interface CollectiveOfferParticipantSectionProps {
  students: StudentLevels[]
}

const CollectiveOfferParticipantSection = ({
  students,
}: CollectiveOfferParticipantSectionProps) => {
  return (
    <SummaryLayout.SubSection title="Participants">
      {students.map(student => (
        <SummaryLayout.Row description={student} key={student} />
      ))}
    </SummaryLayout.SubSection>
  )
}

export default CollectiveOfferParticipantSection
