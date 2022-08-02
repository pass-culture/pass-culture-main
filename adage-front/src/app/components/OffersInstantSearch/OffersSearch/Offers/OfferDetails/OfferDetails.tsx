import React from 'react'

import './OfferDetails.scss'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'api/gen'

import OfferInterventionArea from './OfferInterventionArea'
import OfferSection from './OfferSection'
import OfferVenue from './OfferVenue'

const computeDurationString = (durationMinutes?: number | null) => {
  if (!durationMinutes) return ''
  const hours = Math.floor(durationMinutes / 60)
  const minutes = durationMinutes % 60

  if (hours === 0) {
    return `${minutes}min`
  }

  return `${hours}h${minutes > 0 ? `${minutes}min` : ''}`
}

const computeDisabilityString = (
  audioDisabilityCompliant: boolean,
  mentalDisabilityCompliant: boolean,
  motorDisabilityCompliant: boolean,
  visualDisabilityCompliant: boolean
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

const OfferDetails = ({
  offer,
}: {
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
}): JSX.Element => {
  const {
    durationMinutes,
    venue,
    audioDisabilityCompliant,
    mentalDisabilityCompliant,
    motorDisabilityCompliant,
    visualDisabilityCompliant,
    students,
    offerVenue,
    contactEmail,
    contactPhone,
    educationalPriceDetail,
    interventionArea,
  } = offer

  const durationString = computeDurationString(durationMinutes)
  const displayContactSection = contactEmail || contactPhone
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
      {students?.length > 0 && (
        <OfferSection title="Public Cible">
          <ul className="offer-details-list">
            {students?.map(student => (
              <li key={student}>{student}</li>
            ))}
          </ul>
        </OfferSection>
      )}

      {interventionArea?.length > 0 && (
        <OfferSection title="Zone de Mobiltié de l’acteur culturel">
          <OfferInterventionArea interventionArea={interventionArea} />
        </OfferSection>
      )}

      {educationalPriceDetail && (
        <OfferSection title="Détails">{educationalPriceDetail}</OfferSection>
      )}

      <OfferSection title="Adresse où se déroulera l’évènement">
        <OfferVenue offerVenue={offerVenue} venue={venue} />
      </OfferSection>
      {displayContactSection && (
        <OfferSection title="Contact">
          <ul className="offer-details-list">
            {contactEmail && (
              <li>
                <a
                  className="offer-details-list-item-link"
                  href={`mailto:${contactEmail}`}
                >
                  {contactEmail}
                </a>
              </li>
            )}
            {contactPhone && <li>{contactPhone}</li>}
          </ul>
        </OfferSection>
      )}
      <OfferSection title="Cette offre est accessible aux publics en situation de handicap :">
        {disabilityString}
      </OfferSection>
    </div>
  )
}

export default OfferDetails
