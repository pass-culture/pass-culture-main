import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'

import styles from '../AdageOffer.module.scss'

export type AdageOfferPublicSectionProps = {
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

export function AdageOfferPublicSection({
  offer,
}: AdageOfferPublicSectionProps) {
  const studentLevels = offer.students

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
                <li key={level}>
                  {level}{' '}
                  {i < studentLevels.length - 1 && (
                    <span className={styles['offer-section-group-list-pipe']}>
                      |
                    </span>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            studentLevels[0]
          )}
        </div>
      )}

      <div className={styles['offer-section-group-item']}>
        <h3 className={styles['offer-section-group-item-subtitle']}>
          Accessibilité
        </h3>
        {a11yLevels.length > 0 ? (
          a11yLevels.length > 1 ? (
            <ul className={styles['offer-section-group-list']}>
              {a11yLevels.map((level, i) => (
                <li key={level}>
                  {level}{' '}
                  {i < a11yLevels.length - 1 && (
                    <span className={styles['offer-section-group-list-pipe']}>
                      |
                    </span>
                  )}
                </li>
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
