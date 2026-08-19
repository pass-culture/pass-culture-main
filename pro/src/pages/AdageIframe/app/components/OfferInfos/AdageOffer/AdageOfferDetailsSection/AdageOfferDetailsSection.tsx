import type {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from '@/apiClient/adage'
import { Markdown } from '@/components/Markdown/Markdown'
import { Tag } from '@/design-system/Tag/Tag'

import styles from '../AdageOffer.module.scss'

export type AdageOfferDetailsSectionProps = {
  offer: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
}

const computeDurationString = (durationMinutes?: number | null) => {
  if (!durationMinutes) {
    return ''
  }
  const hours = Math.floor(durationMinutes / 60)
  const minutes = durationMinutes % 60

  if (hours === 0) {
    return `${minutes}min`
  }

  const minutesString = minutes > 0 ? `${minutes}min` : ''
  return `${hours}h${minutesString}`
}

export function AdageOfferDetailsSection({
  offer,
}: AdageOfferDetailsSectionProps) {
  const domains = offer.domains
  const formats = offer.formats
  const duration = computeDurationString(offer.durationMinutes)

  return (
    <>
      {domains.length > 0 && (
        <div className={styles['offer-section-group-item']}>
          <h3 className={styles['offer-section-group-item-subtitle']}>
            Domaines artistiques
          </h3>

          {domains.length > 1 ? (
            <ul className={styles['offer-section-group-list']}>
              {domains.map((domain) => (
                <li key={domain.id}>
                  <Tag label={domain.name} />
                </li>
              ))}
            </ul>
          ) : (
            <Tag label={domains[0].name} />
          )}
        </div>
      )}

      {formats.length > 0 && (
        <div className={styles['offer-section-group-item']}>
          <h3 className={styles['offer-section-group-item-subtitle']}>
            Format de l’offre
          </h3>

          {formats.length > 1 ? (
            <ul className={styles['offer-section-group-list']}>
              {formats.map((format, i) => (
                <li key={format}>
                  {format}{' '}
                  {i < formats.length - 1 && (
                    <span className={styles['offer-section-group-list-pipe']}>
                      |
                    </span>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p className={styles['offer-section-group-item-text']}>
              {formats[0]}
            </p>
          )}
        </div>
      )}

      {offer.nationalProgram && (
        <div className={styles['offer-section-group-item']}>
          <h3 className={styles['offer-section-group-item-subtitle']}>
            Dispositif national
          </h3>
          <p className={styles['offer-section-group-item-text']}>
            {offer.nationalProgram.name}
          </p>
        </div>
      )}

      {duration && (
        <div className={styles['offer-section-group-item']}>
          <h3 className={styles['offer-section-group-item-subtitle']}>Durée</h3>
          <p className={styles['offer-section-group-item-text']}>{duration}</p>
        </div>
      )}

      {offer.description && (
        <div className={styles['offer-section-group-item-description']}>
          <h3 className={styles['offer-section-group-item-subtitle']}>
            Description
          </h3>
          <Markdown markdownText={offer.description} />
        </div>
      )}
    </>
  )
}
