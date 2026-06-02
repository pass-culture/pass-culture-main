import type {
  AuthenticatedResponse,
  CollectiveOfferTemplateResponseModel,
} from '@/apiClient/adage/new'
import {
  computeDistanceInMeters,
  humanizeDistance,
} from '@/commons/utils/getDistance'
import { Banner } from '@/design-system/Banner/Banner'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import strokeInstitutionIcon from '@/icons/stroke-institution.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { ContactButton } from '../../../OffersInstantSearch/OffersSearch/Offers/ContactButton/ContactButton'
import styles from './AdageOfferPartnerPanel.module.scss'

export type AdageOfferPartnerPanelProps = {
  offer: CollectiveOfferTemplateResponseModel
  adageUser?: AuthenticatedResponse
  isPreview?: boolean
  playlistId?: number
}

export function AdageOfferPartnerPanel({
  offer,
  adageUser,
  isPreview = false,
  playlistId,
}: AdageOfferPartnerPanelProps) {
  const venue = offer.venue

  const venueCoords =
    venue.coordinates.latitude != null && venue.coordinates.longitude != null
      ? {
          latitude: venue.coordinates.latitude,
          longitude: venue.coordinates.longitude,
        }
      : null

  const userCoords =
    adageUser?.lat != null && adageUser?.lon != null
      ? { latitude: adageUser.lat, longitude: adageUser.lon }
      : null

  let isFarFromSchool = false
  let distanceText = ''

  if (venueCoords && userCoords) {
    const meters = computeDistanceInMeters(venueCoords, userCoords)
    isFarFromSchool = meters >= 10_000
    distanceText = humanizeDistance(meters)
  }

  return (
    <div className={styles['partner-panel']}>
      <div className={styles['partner-panel-header']}>
        <SvgIcon src={strokeInstitutionIcon} alt="" width="20" />
        <h2 className={styles['partner-panel-header-title']}>
          Partenaire culturel
        </h2>
      </div>
      <div className={styles['partner-panel-info']}>
        {venue.imgUrl ? (
          <img
            src={venue.imgUrl}
            alt=""
            className={styles['partner-panel-info-image']}
          />
        ) : (
          <div className={styles['partner-panel-info-image-fallback']}>
            <SvgIcon src={strokeInstitutionIcon} alt="" width="32" />
          </div>
        )}

        <div>
          <p className={styles['partner-panel-info-name']}>
            {venue.publicName}
          </p>
          {venue.adageId && !isPreview && (
            <Button
              as="a"
              isExternal
              to={`${document.referrer}adage/ressource/partenaires/id/${venue.adageId}`}
              opensInNewTab
              variant={ButtonVariant.TERTIARY}
              color={ButtonColor.NEUTRAL}
              label="Voir la page partenaire"
            />
          )}
        </div>
      </div>

      <div className={styles['partner-panel-location']}>
        {(isPreview || isFarFromSchool) && (
          <Banner
            title="Distance importante"
            description={
              <>
                Ce partenaire est situé{' '}
                {(venue.city || venue.postalCode) &&
                  `à ${venue.city ?? ''} ${venue.postalCode ?? ''},`}
                {`à ${isPreview ? 'X km' : distanceText} de votre établissement scolaire`}
                .
              </>
            }
          />
        )}
      </div>

      <div className={styles['partner-panel-contact']}>
        <ContactButton
          contactEmail={offer.contactEmail}
          contactPhone={offer.contactPhone}
          contactForm={offer.contactForm}
          contactUrl={offer.contactUrl}
          offerId={offer.id}
          queryId={''}
          userEmail={adageUser?.email}
          userRole={adageUser?.role}
          isPreview={isPreview}
          playlistId={playlistId}
        ></ContactButton>
      </div>
    </div>
  )
}
