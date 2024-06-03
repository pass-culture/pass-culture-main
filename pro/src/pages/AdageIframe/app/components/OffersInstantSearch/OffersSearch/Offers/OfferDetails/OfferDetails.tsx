import './OfferDetails.scss'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'

import { getInterventionAreaLabels } from './OfferInterventionArea'
import { OfferSection } from './OfferSection'
import { OfferVenue } from './OfferVenue'

export const computeDurationString = (durationMinutes?: number | null) => {
  if (!durationMinutes) {
    return ''
  }
  const hours = Math.floor(durationMinutes / 60)
  const minutes = durationMinutes % 60

  if (hours === 0) {
    return `${minutes}min`
  }

  return `${hours}h${minutes > 0 ? `${minutes}min` : ''}`
}

const computeDisabilityString = (
  audioDisabilityCompliant?: boolean | null,
  mentalDisabilityCompliant?: boolean | null,
  motorDisabilityCompliant?: boolean | null,
  visualDisabilityCompliant?: boolean | null
): string => {
  const disabilityCompliance: string[] = []
  if (audioDisabilityCompliant) {
    disabilityCompliance.push('Auditif')
  }
  if (mentalDisabilityCompliant) {
    disabilityCompliance.push('Psychique ou cognitif')
  }
  if (motorDisabilityCompliant) {
    disabilityCompliance.push('Moteur')
  }
  if (visualDisabilityCompliant) {
    disabilityCompliance.push('Visuel')
  }

  return disabilityCompliance.join(', ') || 'Non accessible'
}

export const OfferDetails = ({
  offer,
}: {
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
}): JSX.Element => {
  const {
    durationMinutes,
    audioDisabilityCompliant,
    mentalDisabilityCompliant,
    motorDisabilityCompliant,
    visualDisabilityCompliant,
    students,
    offerVenue,
    educationalPriceDetail,
    interventionArea,
    nationalProgram,
  } = offer

  const durationString = computeDurationString(durationMinutes)
  const disabilityString = computeDisabilityString(
    audioDisabilityCompliant,
    mentalDisabilityCompliant,
    motorDisabilityCompliant,
    visualDisabilityCompliant
  )

  return (
    <div className="offer-details">
      {durationString && (
        <OfferSection title="Durée">{durationString}</OfferSection>
      )}
      {students.length > 0 && (
        <OfferSection title="Public Cible">
          <ul className="offer-details-list">
            {students.map((student) => (
              <li key={student}>{student}</li>
            ))}
          </ul>
        </OfferSection>
      )}
      {nationalProgram?.name && (
        <OfferSection title="Dispositif National">
          {nationalProgram.name}
        </OfferSection>
      )}
      {educationalPriceDetail && (
        <OfferSection title="Détails">{educationalPriceDetail}</OfferSection>
      )}

      <OfferSection title="Adresse où se déroulera l’évènement">
        <OfferVenue offerVenue={offerVenue} />
      </OfferSection>

      {interventionArea.length > 0 && (
        <OfferSection title="Zone de Mobilité">
          <div>{getInterventionAreaLabels(interventionArea)}</div>
        </OfferSection>
      )}

      <OfferSection title="Cette offre est accessible aux publics en situation de handicap :">
        {disabilityString}
      </OfferSection>
    </div>
  )
}
