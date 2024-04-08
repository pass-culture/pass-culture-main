import { Link, useSearchParams } from 'react-router-dom'

import {
  AdageFrontRoles,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import strokeOfferIcon from 'icons/stroke-offer.svg'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import { isCollectiveOfferTemplate } from 'pages/AdageIframe/app/types/offers'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { LOGS_DATA } from 'utils/config'

import OfferFavoriteButton from '../OfferFavoriteButton/OfferFavoriteButton'
import OfferShareLink from '../OfferShareLink/OfferShareLink'

import styles from './AdageOfferListCard.module.scss'
import { AdageOfferListCardContent } from './AdageOfferListCardContent/AdageOfferListCardContent'
import { AdageOfferListCardTags } from './AdageOfferListCardTags/AdageOfferListCardTags'

export type AdageOfferListCardProps = {
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
  afterFavoriteChange?: (isFavorite: boolean) => void
  isInSuggestions?: boolean
  queryId?: string
}
export function AdageOfferListCard({
  offer,
  afterFavoriteChange,
  isInSuggestions,
  queryId = '',
}: AdageOfferListCardProps) {
  const [searchParams] = useSearchParams()
  const adageAuthToken = searchParams.get('token')
  const { adageUser } = useAdageUser()

  const isOfferTemplate = isCollectiveOfferTemplate(offer)
  const canAddOfferToFavorites =
    isOfferTemplate && adageUser.role !== AdageFrontRoles.READONLY

  function triggerOfferClickLog(
    offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
  ) {
    if (!LOGS_DATA) {
      return
    }

    if (!isCollectiveOfferTemplate(offer)) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      apiAdage.logOfferDetailsButtonClick({
        iframeFrom: location.pathname,
        stockId: offer.stock.id,
        queryId: queryId,
        isFromNoResult: isInSuggestions,
      })
    } else {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      apiAdage.logOfferTemplateDetailsButtonClick({
        iframeFrom: location.pathname,
        offerId: offer.id,
        queryId: queryId,
        isFromNoResult: isInSuggestions,
      })
    }
  }

  return (
    <div className={styles['offer-card']}>
      <div className={styles['offer-card-image']}>
        {offer.imageUrl ? (
          <img
            alt=""
            className={styles['offer-card-image-img']}
            loading="lazy"
            src={offer.imageUrl}
          />
        ) : (
          <div className={styles['offer-card-image-fallback']}>
            <SvgIcon src={strokeOfferIcon} alt="" />
          </div>
        )}
      </div>
      <div className={styles['offer-card-right']}>
        <div className={styles['offer-card-content']}>
          <AdageOfferListCardTags offer={offer} adageUser={adageUser} />
          <Link
            to={`/adage-iframe/recherche/offre/${offer.id}?token=${adageAuthToken}`}
            state={{ offer }}
            className={styles['offer-card-link']}
            onClick={() => triggerOfferClickLog(offer)}
          >
            <h2 className={styles['offer-title']}>{offer.name}</h2>
          </Link>
          <AdageOfferListCardContent offer={offer} />
        </div>

        <div className={styles['offer-card-actions']}>
          {canAddOfferToFavorites && (
            <OfferFavoriteButton
              offer={offer}
              afterFavoriteChange={afterFavoriteChange}
            />
          )}
          {isOfferTemplate && <OfferShareLink offer={offer} />}
        </div>
      </div>
    </div>
  )
}
