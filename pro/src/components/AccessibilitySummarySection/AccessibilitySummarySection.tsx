import React, { ReactNode } from 'react'

import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { AccessibilityEnum } from 'core/shared'
import { AccessibilityLabel } from 'ui-kit/AccessibilityLabel/AccessibilityLabel'

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
  accessibleWording: string
  callout?: ReactNode
}

export const AccessibilitySummarySection = ({
  accessibleItem,
  accessibleWording,
  callout,
}: AccessibilitySummarySectionProps) => (
  <SummarySubSection title="Modalités d’accessibilité">
    {callout && <div className={styles['callout']}>{callout}</div>}

    {!accessibleItem.visualDisabilityCompliant &&
    !accessibleItem.motorDisabilityCompliant &&
    !accessibleItem.mentalDisabilityCompliant &&
    !accessibleItem.audioDisabilityCompliant ? (
      <SummaryDescriptionList descriptions={[{ text: 'Non accessible' }]} />
    ) : (
      <SummaryDescriptionList descriptions={[{ text: accessibleWording }]} />
    )}

    {accessibleItem.visualDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessibilityEnum.VISUAL}
      />
    )}

    {accessibleItem.mentalDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessibilityEnum.MENTAL}
      />
    )}

    {accessibleItem.motorDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessibilityEnum.MOTOR}
      />
    )}

    {accessibleItem.audioDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessibilityEnum.AUDIO}
      />
    )}
  </SummarySubSection>
)
