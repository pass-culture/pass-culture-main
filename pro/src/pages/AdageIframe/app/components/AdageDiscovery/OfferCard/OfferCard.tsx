import { Link, useSearchParams } from 'react-router-dom'

import { CollectiveOfferTemplateResponseModel } from 'apiClient/adage'
import strokeOfferIcon from 'icons/stroke-offer.svg'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'
import { getHumanizeRelativeDistance } from 'utils/getDistance'

import OfferFavoriteButton from '../../OffersInstantSearch/OffersSearch/Offers/OfferFavoriteButton/OfferFavoriteButton'
import { getOfferTags } from '../../OffersInstantSearch/OffersSearch/Offers/utils/getOfferTags'

import styles from './OfferCard.module.scss'

export interface CardComponentProps {
  offer: CollectiveOfferTemplateResponseModel
  handlePlaylistElementTracking: () => void
}

const OfferCardComponent = ({
  offer,
  handlePlaylistElementTracking,
}: CardComponentProps) => {
  const [searchParams] = useSearchParams()
  const adageAuthToken = searchParams.get('token')
  const { adageUser } = useAdageUser()

  return (
    <div className={styles['container']}>
      <Link
        className={styles['offer-link']}
        data-testid="card-offer-link"
        to={`/adage-iframe/decouverte/offre/${offer.id}?token=${adageAuthToken}`}
        state={{ offer }}
        onClick={() => {
          handlePlaylistElementTracking()
        }}
      >
        <div className={styles['offer-image-container']}>
          {offer.imageUrl ? (
            <img
              alt=""
              className={styles['offer-image']}
              loading="lazy"
              src={offer.imageUrl}
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
                variant={TagVariant.LIGHT_GREY}
                className={styles['offer-tag']}
              >
                <span aria-hidden="true">{tag.icon}</span> {tag.text}
              </Tag>
            )
          })}
        </div>

        <div
          className={styles['offer-name']}
          title={offer.name}
          data-testid="card-offer"
        >
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
      <OfferFavoriteButton
        offer={{ ...offer, isTemplate: true }}
        className={styles['offer-favorite-button']}
      />
    </div>
  )
}

export default OfferCardComponent
