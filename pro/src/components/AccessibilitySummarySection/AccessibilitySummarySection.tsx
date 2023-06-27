import React from 'react'

import { SummaryLayout } from 'components/SummaryLayout'
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
  <SummaryLayout.SubSection title="Accessibilité">
    {noDisabilityCompliance && (
      <SummaryLayout.Row description="Non accessible" />
    )}
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
  </SummaryLayout.SubSection>
)

export default AccessibilitySummarySection
