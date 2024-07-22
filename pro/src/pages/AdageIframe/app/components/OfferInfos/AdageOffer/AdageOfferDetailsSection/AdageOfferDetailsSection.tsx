import {
  CollectiveOfferTemplateResponseModel,
  CollectiveOfferResponseModel,
} from 'apiClient/adage'
import { Markdown } from 'components/Markdown/Markdown'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

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

  return `${hours}h${minutes > 0 ? `${minutes}min` : ''}`
}

export function AdageOfferDetailsSection({
  offer,
}: AdageOfferDetailsSectionProps) {
  const domains = offer.domains
  const formats = offer.formats || []
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
                  <Tag variant={TagVariant.LIGHT_GREY}>{domain.name}</Tag>
                </li>
              ))}
            </ul>
          ) : (
            <Tag variant={TagVariant.LIGHT_GREY}>{domains[0]?.name}</Tag>
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
            formats[0]
          )}
        </div>
      )}

      {offer.nationalProgram && (
        <div className={styles['offer-section-group-item']}>
          <h3 className={styles['offer-section-group-item-subtitle']}>
            Dispositif national
          </h3>
          {offer.nationalProgram.name}
        </div>
      )}

      {duration && (
        <div className={styles['offer-section-group-item']}>
          <h3 className={styles['offer-section-group-item-subtitle']}>Durée</h3>
          {duration}
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
