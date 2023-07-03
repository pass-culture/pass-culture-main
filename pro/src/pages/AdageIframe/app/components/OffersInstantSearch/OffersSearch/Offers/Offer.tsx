import cn from 'classnames'
import React, { useState } from 'react'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import DialogBox from 'components/DialogBox/DialogBox'
import useActiveFeature from 'hooks/useActiveFeature'
import fullLikeIcon from 'icons/full-like.svg'
import { ReactComponent as ChevronIconAdage } from 'icons/ico-chevron-adage.svg'
import { ReactComponent as ImagePlaceholder } from 'icons/ico-placeholder-offer-image.svg'
import { ReactComponent as StrokeLikeIcon } from 'icons/stroke-like.svg'
import strokePassIcon from 'icons/stroke-pass.svg'
import {
  HydratedCollectiveOffer,
  HydratedCollectiveOfferTemplate,
  isCollectiveOffer,
} from 'pages/AdageIframe/app/types/offers'
import { Button, Tag } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { LOGS_DATA } from 'utils/config'
import { removeParamsFromUrl } from 'utils/removeParamsFromUrl'

import ContactButton from './ContactButton'
import style from './Offer.module.scss'
import OfferDetails from './OfferDetails/OfferDetails'
import OfferSummary from './OfferSummary/OfferSummary'
import PrebookingButton from './PrebookingButton/PrebookingButton'
import { formatDescription } from './utils/formatDescription'
import { getOfferVenueAndOffererName } from './utils/getOfferVenueAndOffererName'

export interface OfferProps {
  offer: HydratedCollectiveOffer | HydratedCollectiveOfferTemplate
  queryId: string
  position: number
  userEmail?: string | null
  userRole: AdageFrontRoles
}

const Offer = ({
  offer,
  queryId,
  position,
  userEmail,
  userRole,
}: OfferProps): JSX.Element => {
  const [displayDetails, setDisplayDetails] = useState(false)
  const [isModalLikeOpen, setIsModalLikeOpen] = useState(false)
  const isLikeActive = useActiveFeature('WIP_ENABLE_LIKE_IN_ADAGE')

  const openOfferDetails = (
    offer: HydratedCollectiveOffer | HydratedCollectiveOfferTemplate
  ) => {
    if (LOGS_DATA) {
      !offer.isTemplate
        ? apiAdage.logOfferDetailsButtonClick({
            AdageHeaderFrom: removeParamsFromUrl(location.pathname),
            stockId: offer.stock.id,
          })
        : apiAdage.logOfferTemplateDetailsButtonClick({
            AdageHeaderFrom: removeParamsFromUrl(location.pathname),
            offerId: offer.id,
          })
    }
    setDisplayDetails(!displayDetails)
  }

  const handleLikeClick = () => {
    apiAdage.logFavOfferButtonClick({
      AdageHeaderFrom: removeParamsFromUrl(location.pathname),
      offerId: offer.id,
    })
    setIsModalLikeOpen(true)
  }

  return (
    <li className={style['offer']} data-testid="offer-listitem">
      <div
        className={cn(style['offer-logo-placeholder'], {
          [style['offer-logo-placeholder-showcase']]: offer.isTemplate,
        })}
        data-testid="thumb-placeholder"
      >
        <SvgIcon
          src={strokePassIcon}
          alt=""
          className={style['ico-logo-passculture']}
        />
      </div>
      <div className={style['offer-main-container']}>
        <div className={style['offer-image-container']}>
          {offer.imageUrl ? (
            <img
              alt=""
              className={style['offer-image']}
              loading="lazy"
              src={offer.imageUrl}
            />
          ) : (
            <div className={style['offer-image-default']}>
              <ImagePlaceholder />
            </div>
          )}
        </div>
        <div className={style['offer-container']}>
          {offer.isTemplate ? (
            <ContactButton
              className={style['offer-prebooking-button']}
              contactEmail={offer.contactEmail}
              contactPhone={offer.contactPhone}
              venueName={offer.venue.publicName || offer.venue.name}
              offererName={offer.venue.managingOfferer.name}
              offerId={offer.id}
              position={position}
              queryId={queryId}
              userEmail={userEmail}
              userRole={userRole}
            />
          ) : (
            <PrebookingButton
              canPrebookOffers={userRole == AdageFrontRoles.REDACTOR}
              className={style['offer-prebooking-button']}
              offerId={offer.id}
              queryId={queryId}
              stock={offer.stock}
            />
          )}
          <div className={style['offer-header']}>
            <h2 className={style['offer-header-title']}>{offer.name}</h2>
            <div className={style['offer-header-subtitles']}>
              <span className={style['offer-header-label']}>Proposée par </span>
              <span>{getOfferVenueAndOffererName(offer.venue)}</span>
            </div>
            {isCollectiveOffer(offer) && offer.teacher && (
              <div className={style['offer-header-subtitles']}>
                <span className={style['offer-header-label']}>Destinée à </span>
                <span>
                  {offer.teacher.firstName} {offer.teacher.lastName}
                </span>
              </div>
            )}
            <ul className={style['offer-domains-list']}>
              {offer?.domains?.map(domain => (
                <li
                  className={style['offer-domains-list-item']}
                  key={domain.id}
                >
                  <Tag
                    label={domain.name}
                    className={style['offer-domains-tag']}
                  />
                </li>
              ))}
            </ul>
          </div>
          <OfferSummary offer={offer} />
          <p className={style['offer-description']}>
            {formatDescription(offer.description)}
          </p>
          <div className={style['offer-footer']}>
            <button
              className={style['offer-see-more']}
              onClick={() => openOfferDetails(offer)}
              type="button"
            >
              <ChevronIconAdage
                className={cn(style['offer-see-more-icon'], {
                  [style['offer-see-more-icon-closed']]: !displayDetails,
                })}
              />
              en savoir plus
            </button>
            {isLikeActive && (
              <Button
                Icon={StrokeLikeIcon}
                className={style['offer-like-button']}
                title="bouton j'aime"
                variant={ButtonVariant.TERNARY}
                onClick={handleLikeClick}
              />
            )}
            {isModalLikeOpen && (
              <DialogBox
                labelledBy="aimer une offre"
                extraClassNames={style['offer-like-modal']}
                hasCloseButton
              >
                <SvgIcon
                  src={fullLikeIcon}
                  alt=""
                  width="88"
                  className={style['full-like-icon']}
                />
                <p className={style['offer-like-modal-text']}>
                  Lʼéquipe du pass Culture a bien noté votre intérêt pour cette
                  fonctionnalité. Elle arrivera bientôt !
                </p>
                <Button
                  onClick={() => setIsModalLikeOpen(false)}
                  className={style['offer-like-modal-button']}
                >
                  Fermer
                </Button>
              </DialogBox>
            )}
          </div>

          {displayDetails && <OfferDetails offer={offer} />}
        </div>
      </div>
    </li>
  )
}
export default Offer
