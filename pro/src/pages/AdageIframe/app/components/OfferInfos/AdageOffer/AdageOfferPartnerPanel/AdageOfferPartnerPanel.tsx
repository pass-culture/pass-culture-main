import {
  AuthenticatedResponse,
  CollectiveOfferTemplateResponseModel,
} from '@/apiClient/adage'
import { getHumanizeRelativeDistance } from '@/commons/utils/getDistance'
import fullLinkIcon from '@/icons/full-link.svg'
import strokeInstitutionIcon from '@/icons/stroke-institution.svg'
import { ButtonLink } from '@/ui-kit/Button/ButtonLink'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { Callout } from '@/ui-kit/Callout/Callout'
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

  const distanceToSchool =
    venue.coordinates.latitude !== null &&
    venue.coordinates.latitude !== undefined &&
    venue.coordinates.longitude !== null &&
    venue.coordinates.longitude !== undefined &&
    adageUser &&
    adageUser.lat !== null &&
    adageUser.lat !== undefined &&
    adageUser.lon !== null &&
    adageUser.lon !== undefined &&
    getHumanizeRelativeDistance(
      {
        latitude: venue.coordinates.latitude,
        longitude: venue.coordinates.longitude,
      },
      {
        latitude: adageUser.lat,
        longitude: adageUser.lon,
      }
    )

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
          <p className={styles['partner-panel-info-name']}>{venue.name}</p>
          {venue.adageId && !isPreview && (
            <ButtonLink
              isExternal
              to={`${document.referrer}adage/ressource/partenaires/id/${venue.adageId}`}
              opensInNewTab
              variant={ButtonVariant.TERNARY}
              className={styles['partner-panel-info-link']}
              icon={fullLinkIcon}
            >
              Voir la page partenaire
            </ButtonLink>
          )}
        </div>
      </div>

      <div className={styles['partner-panel-location']}>
        {(venue.city || venue.postalCode || distanceToSchool || isPreview) && (
          <Callout>
            Ce partenaire est situé{' '}
            {(venue.city || venue.postalCode) &&
              `à ${venue.city ?? ''} ${venue.postalCode ?? ''}, `}
            {(isPreview || distanceToSchool) &&
              `à ${isPreview ? 'X km' : distanceToSchool} de votre
            établissement scolaire`}
            .
          </Callout>
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
