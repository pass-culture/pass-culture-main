import {
  CollectiveOfferTemplateResponseModel,
  CollectiveOfferResponseModel,
} from 'apiClient/adage'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import { computeDurationString } from '../../../OffersInstantSearch/OffersSearch/Offers/OfferDetails/OfferDetails'
import styles from '../AdageOffer.module.scss'

type AdageOfferDetailsSectionProps = {
  offer: CollectiveOfferTemplateResponseModel | CollectiveOfferResponseModel
}

export default function AdageOfferDetailsSection({
  offer,
}: AdageOfferDetailsSectionProps) {
  const domains = offer.domains || []
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
            <Tag variant={TagVariant.LIGHT_GREY}>{domains[0].name}</Tag>
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
                <>
                  <li key={format}>{format}</li>{' '}
                  {i < formats.length - 1 && (
                    <span className={styles['offer-section-group-list-pipe']}>
                      |
                    </span>
                  )}
                </>
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
        <div className={styles['offer-section-group-item']}>
          <h3 className={styles['offer-section-group-item-subtitle']}>
            Description
          </h3>
          {offer.description}
        </div>
      )}
    </>
  )
}
