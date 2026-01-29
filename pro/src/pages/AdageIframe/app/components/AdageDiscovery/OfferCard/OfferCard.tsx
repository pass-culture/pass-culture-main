import { Link, useLocation, useNavigate, useSearchParams } from 'react-router'

import type { CollectiveOfferTemplateResponseModel } from '@/apiClient/adage'
import { getHumanizeRelativeDistance } from '@/commons/utils/getDistance'
import { Tag, TagVariant } from '@/design-system/Tag/Tag'
import strokeOfferIcon from '@/icons/stroke-offer.svg'
import { useAdageUser } from '@/pages/AdageIframe/app/hooks/useAdageUser'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { OfferFavoriteButton } from '../../OffersInstantSearch/OffersSearch/Offers/OfferFavoriteButton/OfferFavoriteButton'
import { getOfferTags } from '../../OffersInstantSearch/OffersSearch/Offers/utils/getOfferTags'
import styles from './OfferCard.module.scss'

export interface CardComponentProps {
  offer: CollectiveOfferTemplateResponseModel
  onCardClicked: () => void
  viewType?: 'grid' | 'list'
  playlistId?: number
}

export const OfferCardComponent = ({
  offer,
  onCardClicked,
  viewType,
  playlistId,
}: CardComponentProps) => {
  const location = useLocation()

  const currentPathname = location.pathname.split('/')[2]
  const [searchParams] = useSearchParams()
  const adageAuthToken = searchParams.get('token')
  const { adageUser } = useAdageUser()
  const navigate = useNavigate()

  const offerLinkUrl =
    document.referrer && !document.referrer.includes('adage-iframe')
      ? `${document.referrer}adage/passculture/offres/offerid/${offer.isTemplate ? '' : 'B-'}${offer.id}`
      : `/adage-iframe/${currentPathname}/offre/${offer.id}?token=${adageAuthToken}`

  return (
    <div className={styles['container']}>
      <Link
        onClick={(e) => {
          onCardClicked()
          if (!e.metaKey) {
            e.preventDefault()
            // eslint-disable-next-line @typescript-eslint/no-floating-promises
            navigate(`offre/${offer.id}?token=${adageAuthToken}`, {
              state: { offer, playlistId },
            })
          }
        }}
        className={styles['offer-link']}
        data-testid="card-offer-link"
        to={offerLinkUrl}
        target="_parent"
        state={{ offer }}
      >
        <div className={styles['offer-image-container']}>
          {offer.imageUrl ? (
            <img
              alt=""
              className={styles['offer-image']}
              loading="lazy"
              src={offer.imageUrl}
              width={216}
            />
          ) : (
            <div
              className={`${styles['offer-image']} ${styles['offer-image-fallback']}`}
            >
              <SvgIcon src={strokeOfferIcon} alt="" width="80" />
            </div>
          )}
        </div>

        <div className={styles['offer-tag-container']}>
          {getOfferTags(offer, adageUser, false).map((tag) => {
            return (
              <Tag
                key={tag.text}
                label={tag.text}
                icon={tag.icon}
                variant={TagVariant.DEFAULT}
              />
            )
          })}
        </div>

        <div className={styles['offer-name']} data-testid="card-offer">
          {offer.name}
        </div>

        <div className="offer-venue">
          <div className={styles['offer-venue-name']}>{offer.venue.name}</div>
          {offer.venue.coordinates.latitude &&
            offer.venue.coordinates.longitude &&
            (adageUser.lat || adageUser.lat === 0) &&
            (adageUser.lon || adageUser.lon === 0) && (
              <div
                className={styles['offer-venue-distance']}
              >{`à ${getHumanizeRelativeDistance(
                {
                  latitude: offer.venue.coordinates.latitude,
                  longitude: offer.venue.coordinates.longitude,
                },
                {
                  latitude: adageUser.lat,
                  longitude: adageUser.lon,
                }
              )} - ${offer.venue.city}`}</div>
            )}
        </div>
      </Link>
      <div className={styles['offer-favorite-button-container']}>
        <OfferFavoriteButton
          offer={{ ...offer, isTemplate: true }}
          viewType={viewType}
          playlistId={playlistId}
        />
      </div>
    </div>
  )
}
