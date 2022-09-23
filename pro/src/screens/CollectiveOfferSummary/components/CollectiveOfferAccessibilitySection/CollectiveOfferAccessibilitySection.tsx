import React from 'react'

import { GetCollectiveOfferTemplateResponseModel } from 'apiClient/v1'
import { AccessiblityEnum } from 'core/shared'
import { SummaryLayout } from 'new_components/SummaryLayout'
import { AccessibilityLabel } from 'ui-kit/AccessibilityLabel'

import styles from './CollectiveOfferAccessibilitySection.module.scss'

interface ICollectiveOfferParticipantSectionProps {
  offer: GetCollectiveOfferTemplateResponseModel
}

const CollectiveOfferParticipantSection = ({
  offer,
}: ICollectiveOfferParticipantSectionProps) => {
  const noDisabilityCompliance =
    !offer.audioDisabilityCompliant &&
    !offer.motorDisabilityCompliant &&
    !offer.mentalDisabilityCompliant &&
    !offer.visualDisabilityCompliant

  return (
    <SummaryLayout.SubSection title="Accessibilité">
      {noDisabilityCompliance && (
        <SummaryLayout.Row description="Non accessible" />
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
    </SummaryLayout.SubSection>
  )
}

export default CollectiveOfferParticipantSection
