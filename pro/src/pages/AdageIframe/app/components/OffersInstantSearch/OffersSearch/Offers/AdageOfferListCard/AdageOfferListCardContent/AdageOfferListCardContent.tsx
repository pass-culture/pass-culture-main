import {
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from '@/apiClient/adage'
import { Markdown } from '@/components/Markdown/Markdown'

import { getOfferVenueAndOffererName } from '../../utils/getOfferVenueAndOffererName'
import styles from './AdageOfferListCardContent.module.scss'

export type AdageOfferListCardContentProps = {
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
}

export function AdageOfferListCardContent({
  offer,
}: AdageOfferListCardContentProps) {
  const description = offer.description ?? ''
  return (
    <>
      <p className={styles['offer-offerer']}>
        {getOfferVenueAndOffererName(offer.venue)}
      </p>
      {offer.formats.length && (
        <div className={styles['offer-formats']}>
          {offer.formats.length === 1 ? (
            <span className={styles['offer-formats-format']}>
              {offer.formats[0]}
            </span>
          ) : (
            <ul className={styles['offer-formats-list']}>
              {offer.formats.map((format, i) => (
                <li key={format}>
                  {i > 0 && (
                    <span className={styles['offer-formats-list-pipe']}>|</span>
                  )}
                  <span className={styles['offer-formats-format']}>
                    {format}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
      {description && (
        <p
          className={styles['offer-description']}
          data-testid="offer-description"
        >
          <Markdown markdownText={description} />
        </p>
      )}
    </>
  )
}
