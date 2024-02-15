import React from 'react'

import { SummaryRow } from 'components/SummaryLayout/SummaryRow'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { CollectiveOfferTemplate, CollectiveOffer } from 'core/OfferEducational'
import { IndividualOffer } from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'
import { AccessibilityLabel } from 'ui-kit/AccessibilityLabel'

import styles from './AccessibilitySummarySection.module.scss'

interface AccessibilitySummarySectionProps {
  offer: IndividualOffer | CollectiveOfferTemplate | CollectiveOffer
}

const AccessibilitySummarySection = ({
  offer,
}: AccessibilitySummarySectionProps) => (
  <SummarySubSection title="Accessibilité">
    {!offer.visualDisabilityCompliant &&
      !offer.motorDisabilityCompliant &&
      !offer.mentalDisabilityCompliant &&
      !offer.audioDisabilityCompliant && (
        <SummaryRow description="Non accessible" />
      )}

    {offer.visualDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessiblityEnum.VISUAL}
      />
    )}

    {offer.mentalDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessiblityEnum.MENTAL}
      />
    )}

    {offer.motorDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessiblityEnum.MOTOR}
      />
    )}

    {offer.audioDisabilityCompliant && (
      <AccessibilityLabel
        className={styles['accessibility-row']}
        name={AccessiblityEnum.AUDIO}
      />
    )}
  </SummarySubSection>
)

export default AccessibilitySummarySection
