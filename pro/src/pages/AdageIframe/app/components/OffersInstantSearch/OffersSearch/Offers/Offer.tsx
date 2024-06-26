import cn from 'classnames'
import { useState } from 'react'

import {
  AdageFrontRoles,
  CollectiveOfferResponseModel,
  CollectiveOfferTemplateResponseModel,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { Markdown } from 'components/Markdown/Markdown'
import fullLinkIcon from 'icons/full-link.svg'
import strokeOfferIcon from 'icons/stroke-offer.svg'
import { useAdageUser } from 'pages/AdageIframe/app/hooks/useAdageUser'
import {
  isCollectiveOfferBookable,
  isCollectiveOfferTemplate,
} from 'pages/AdageIframe/app/types'
import { ButtonLink } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

import style from './Offer.module.scss'
import { OfferFavoriteButton } from './OfferFavoriteButton/OfferFavoriteButton'
import { OfferShareLink } from './OfferShareLink/OfferShareLink'
import { OfferSummary } from './OfferSummary/OfferSummary'
import { PrebookingButton } from './PrebookingButton/PrebookingButton'
import { getOfferVenueAndOffererName } from './utils/getOfferVenueAndOffererName'

export interface OfferProps {
  offer: CollectiveOfferResponseModel | CollectiveOfferTemplateResponseModel
  queryId: string
  position: number
  afterFavoriteChange?: (isFavorite: boolean) => void
  isInSuggestions?: boolean
  openDetails?: boolean
}

export const Offer = ({
  offer,
  queryId,
  afterFavoriteChange,
  isInSuggestions,
}: OfferProps): JSX.Element => {
  const [offerPrebooked, setOfferPrebooked] = useState(false)
  const { adageUser, setInstitutionOfferCount, institutionOfferCount } =
    useAdageUser()

  const canAddOfferToFavorites =
    offer.isTemplate && adageUser.role !== AdageFrontRoles.READONLY

  function offerVenueLinkClicked() {
    void apiAdage.logTrackingMap({
      iframeFrom: location.pathname,
    })
  }

  const venueAndOffererName = getOfferVenueAndOffererName(offer.venue)

  return (
    <div className={style['offer']}>
      {isCollectiveOfferBookable(offer) && (
        <div
          className={cn(style['offer-headband'], {
            [style['offer-headband-prebooked']]: offerPrebooked,
          })}
        >
          <div className={style['offer-headband-text']}>
            <span className={style['intended-for']}>Offre destinée à :</span>
            {offer.teacher && (
              <span
                className={style['infos']}
              >{`${offer.teacher.civility} ${offer.teacher.lastName} ${offer.teacher.firstName}`}</span>
            )}
            <span className={style['infos']}>
              {offer.educationalInstitution?.institutionType}{' '}
              {offer.educationalInstitution?.name}
            </span>
          </div>

          <PrebookingButton
            canPrebookOffers={adageUser.role === AdageFrontRoles.REDACTOR}
            className={style['offer-prebooking-button']}
            offerId={offer.id}
            queryId={queryId}
            stock={offer.stock}
            isInSuggestions={isInSuggestions}
            setOfferPrebooked={(value: boolean) => setOfferPrebooked(value)}
            setInstitutionOfferCount={setInstitutionOfferCount}
            institutionOfferCount={institutionOfferCount}
          />
        </div>
      )}
      <div className={style['offer-container']}>
        <div className={style['offer-image-container']}>
          {offer.imageUrl ? (
            <img
              alt=""
              className={style['offer-image']}
              loading="lazy"
              src={offer.imageUrl}
              width={216}
            />
          ) : (
            <div className={style['offer-image-default']}>
              <SvgIcon src={strokeOfferIcon} alt="" />
            </div>
          )}
        </div>
        <div className={style['offer-details-container']}>
          <div className={style['offer-header']}>
            <div className={style['offer-header-row']}>
              <h2 className={style['offer-header-row-title']}>{offer.name}</h2>
              <div className={style['offer-details-actions']}>
                {canAddOfferToFavorites && (
                  <OfferFavoriteButton
                    offer={offer}
                    afterFavoriteChange={afterFavoriteChange}
                    queryId={queryId}
                  />
                )}
                {isCollectiveOfferTemplate(offer) && (
                  <>
                    <OfferShareLink offer={offer} />
                  </>
                )}
              </div>
            </div>

            <div className={style['offer-header-subtitles']}>
              <span className={style['offer-header-label']}>Proposée par</span>

              {offer.venue.adageId ? (
                <ButtonLink
                  link={{
                    isExternal: true,
                    to: `${document.referrer}adage/ressource/partenaires/id/${offer.venue.adageId}`,
                    target: '_blank',
                  }}
                  variant={ButtonVariant.TERNARY}
                  className={style['offer-header-venue-link']}
                  onClick={offerVenueLinkClicked}
                  icon={fullLinkIcon}
                >
                  {venueAndOffererName}
                </ButtonLink>
              ) : (
                <span>{venueAndOffererName}</span>
              )}
            </div>
            {isCollectiveOfferBookable(offer) && offer.teacher && (
              <div className={style['offer-header-teacher']}>
                <span className={style['offer-header-label']}>Destinée à </span>
                <span>
                  {offer.teacher.firstName} {offer.teacher.lastName}
                </span>
              </div>
            )}
            <ul className={style['offer-domains-list']}>
              {offer.domains.map((domain) => (
                <li
                  className={style['offer-domains-list-item']}
                  key={domain.id}
                >
                  <Tag
                    variant={TagVariant.LIGHT_GREY}
                    className={style['offer-domains-list-item-tag']}
                  >
                    {domain.name}
                  </Tag>
                </li>
              ))}
            </ul>
          </div>
          <OfferSummary offer={offer} />
          {offer.description && (
            <p className={style['offer-description']}>
              <Markdown markdownText={offer.description} />
            </p>
          )}
          <ButtonLink
            variant={
              offer.isTemplate ? ButtonVariant.PRIMARY : ButtonVariant.SECONDARY
            }
            link={{
              isExternal: true,
              to: `${document.referrer}adage/passculture/offres/offerid/${offer.isTemplate ? '' : 'B-'}${offer.id}`,
              target: '_blank',
            }}
            icon={fullLinkIcon}
            svgAlt="Nouvelle fenêtre"
          >
            Découvrir l’offre
          </ButtonLink>
        </div>
      </div>
    </div>
  )
}
