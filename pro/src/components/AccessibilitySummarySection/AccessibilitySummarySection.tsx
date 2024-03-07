import React from 'react'

import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { AccessiblityEnum } from 'core/shared'
import { AccessibilityLabel } from 'ui-kit/AccessibilityLabel'

import styles from './AccessibilitySummarySection.module.scss'

// This interface is verified by both collective/individual offers and venues
interface AccessibleItem {
  audioDisabilityCompliant?: boolean | null
  mentalDisabilityCompliant?: boolean | null
  motorDisabilityCompliant?: boolean | null
  visualDisabilityCompliant?: boolean | null
}

interface AccessibilitySummarySectionProps {
  accessibleItem: AccessibleItem
}

export const AccessibilitySummarySection = ({
  accessibleItem,
}: AccessibilitySummarySectionProps) => (
  <SummarySubSection title="Modalités d’accessibilité">
    {!accessibleItem.visualDisabilityCompliant &&
      !accessibleItem.motorDisabilityCompliant &&
      !accessibleItem.mentalDisabilityCompliant &&
      !accessibleItem.audioDisabilityCompliant && (
        <SummaryDescriptionList descriptions={[{ text: 'Non accessible' }]} />
      )}

    {accessibleItem.visualDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessiblityEnum.VISUAL}
      />
    )}

    {accessibleItem.mentalDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessiblityEnum.MENTAL}
      />
    )}

    {accessibleItem.motorDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessiblityEnum.MOTOR}
      />
    )}

    {accessibleItem.audioDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessiblityEnum.AUDIO}
      />
    )}
  </SummarySubSection>
)
