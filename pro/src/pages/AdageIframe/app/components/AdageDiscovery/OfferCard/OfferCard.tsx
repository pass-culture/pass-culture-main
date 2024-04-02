import { Link, useSearchParams } from 'react-router-dom'

import { CollectiveOfferTemplateResponseModel } from 'apiClient/adage'
import { OfferAddressType } from 'apiClient/v1'
import strokeOfferIcon from 'icons/stroke-offer.svg'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'
import {
  humanizeDistance,
  getHumanizeRelativeDistance,
} from 'utils/getDistance'

import OfferFavoriteButton from '../../OffersInstantSearch/OffersSearch/Offers/OfferFavoriteButton/OfferFavoriteButton'

import logoSchoolTrip from './assets/icon-school-trip.svg'
import logoSchool from './assets/icon-school.svg'
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

  const tagInfos = {
    [OfferAddressType.SCHOOL]: [{ logo: logoSchool, text: 'En classe' }],
    [OfferAddressType.OFFERER_VENUE]: [
      { logo: logoSchoolTrip, text: 'Sortie' },
      {
        text:
          offer.offerVenue.distance || offer.offerVenue.distance === 0
            ? `À ${humanizeDistance(offer.offerVenue.distance * 1000)}`
            : null,
      },
    ],
    [OfferAddressType.OTHER]: [
      { logo: logoSchoolTrip, text: 'Sortie' },
      { text: 'Lieu à définir' },
    ],
  }

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
          {tagInfos[offer.offerVenue.addressType].map((elm, index) => {
            return (
              elm.text && (
                <Tag
                  key={`tag-${index}`}
                  variant={TagVariant.LIGHT_GREY}
                  className={styles['offer-tag']}
                >
                  {elm.logo && (
                    <img
                      alt=""
                      src={elm.logo}
                      className={styles['offer-tag-image']}
                    />
                  )}
                  <span>{elm.text}</span>
                </Tag>
              )
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
