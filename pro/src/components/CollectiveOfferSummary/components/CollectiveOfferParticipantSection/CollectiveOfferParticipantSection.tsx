import React from 'react'

import { StudentLevels } from 'apiClient/v1'
import { SummaryRow } from 'components/SummaryLayout/SummaryRow'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

interface CollectiveOfferParticipantSectionProps {
  students: StudentLevels[]
}

const CollectiveOfferParticipantSection = ({
  students,
}: CollectiveOfferParticipantSectionProps) => {
  return (
    <SummarySubSection title="Participants">
      {students.map((student) => (
        <SummaryRow description={student} key={student} />
      ))}
    </SummarySubSection>
  )
}

export default CollectiveOfferParticipantSection
