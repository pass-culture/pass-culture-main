import React from 'react'

import { SummaryRow } from 'components/SummaryLayout/SummaryRow'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { AccessiblityEnum } from 'core/shared'
import { AccessibilityLabel } from 'ui-kit/AccessibilityLabel'

import styles from './AccessibilitySummarySection.module.scss'

interface AccessibilitySummarySectionProps {
  noDisabilityCompliance: boolean
  visualDisabilityCompliant: boolean
  mentalDisabilityCompliant: boolean
  motorDisabilityCompliant: boolean
  audioDisabilityCompliant: boolean
}

const AccessibilitySummarySection = ({
  noDisabilityCompliance,
  visualDisabilityCompliant,
  mentalDisabilityCompliant,
  motorDisabilityCompliant,
  audioDisabilityCompliant,
}: AccessibilitySummarySectionProps) => (
  <SummarySubSection title="Accessibilité">
    {noDisabilityCompliance && <SummaryRow description="Non accessible" />}
    {visualDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessiblityEnum.VISUAL}
      />
    )}
    {mentalDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessiblityEnum.MENTAL}
      />
    )}
    {motorDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessiblityEnum.MOTOR}
      />
    )}
    {audioDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessiblityEnum.AUDIO}
      />
    )}
  </SummarySubSection>
)

export default AccessibilitySummarySection
