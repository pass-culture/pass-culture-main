import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'

import styles from '../AdageOffer.module.scss'

type AdageOfferPublicSectionProps = {
  offer: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
}

const getAccessibilityLevels = ({
  audioDisabilityCompliant,
  mentalDisabilityCompliant,
  motorDisabilityCompliant,
  visualDisabilityCompliant,
}: AdageOfferPublicSectionProps['offer']): string[] => {
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

  return disabilityCompliance
}

export default function AdageOfferPublicSection({
  offer,
}: AdageOfferPublicSectionProps) {
  const studentLevels = offer.students || []

  const a11yLevels = getAccessibilityLevels(offer)

  return (
    <>
      {studentLevels.length > 0 && (
        <div className={styles['offer-section-group-item']}>
          <h3 className={styles['offer-section-group-item-subtitle']}>
            Niveau scolaire
          </h3>

          {studentLevels.length > 1 ? (
            <ul className={styles['offer-section-group-list']}>
              {studentLevels.map((level, i) => (
                <>
                  <li key={level}>{level}</li>{' '}
                  {i < level.length - 1 && (
                    <span className={styles['offer-section-group-list-pipe']}>
                      |
                    </span>
                  )}
                </>
              ))}
            </ul>
          ) : (
            studentLevels[0]
          )}
        </div>
      )}

      <div className={styles['offer-section-group-item']}>
        <h3 className={styles['offer-section-group-item-subtitle']}>
          Cette offre est accessible aux publics en situation de handicap
        </h3>
        {a11yLevels.length > 0 ? (
          a11yLevels.length > 1 ? (
            <ul className={styles['offer-section-group-list']}>
              {a11yLevels.map((level, i) => (
                <>
                  <li key={level}>{level}</li>{' '}
                  {i < level.length - 1 && (
                    <span className={styles['offer-section-group-list-pipe']}>
                      |
                    </span>
                  )}
                </>
              ))}
            </ul>
          ) : (
            a11yLevels[0]
          )
        ) : (
          'Non accessible'
        )}
      </div>
    </>
  )
}
