import React, { ReactNode } from 'react'

import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { AccessibilityEnum } from 'core/shared/types'
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
}: AccessibilitySummarySectionProps) => {
  const {
    visualDisabilityCompliant,
    motorDisabilityCompliant,
    mentalDisabilityCompliant,
    audioDisabilityCompliant,
  } = accessibleItem
  const isAccessible =
    visualDisabilityCompliant ||
    motorDisabilityCompliant ||
    mentalDisabilityCompliant ||
    audioDisabilityCompliant
  return (
    <SummarySubSection title="Modalités d’accessibilité">
      {callout && <div className={styles['callout']}>{callout}</div>}
      <SummaryDescriptionList
        descriptions={[
          { text: !isAccessible ? 'Non accessible' : accessibleWording },
        ]}
      />
      {isAccessible && (
        <ul className={styles['accessibility-list']}>
          {visualDisabilityCompliant && (
            <li>
              <AccessibilityLabel name={AccessibilityEnum.VISUAL} />
            </li>
          )}
          {mentalDisabilityCompliant && (
            <li>
              <AccessibilityLabel name={AccessibilityEnum.MENTAL} />
            </li>
          )}
          {motorDisabilityCompliant && (
            <li>
              <AccessibilityLabel name={AccessibilityEnum.MOTOR} />
            </li>
          )}
          {audioDisabilityCompliant && (
            <li>
              <AccessibilityLabel name={AccessibilityEnum.AUDIO} />
            </li>
          )}
        </ul>
      )}
    </SummarySubSection>
  )
}
