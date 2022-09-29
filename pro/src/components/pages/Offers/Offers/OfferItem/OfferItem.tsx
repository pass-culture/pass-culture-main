import React from 'react'
import { Link } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import useAnalytics from 'components/hooks/useAnalytics'
import {
  useOfferEditionURL,
  useOfferStockEditionURL,
} from 'components/hooks/useOfferEditionURL'
import Icon from 'components/layout/Icon'
import { isOfferDisabled } from 'components/pages/Offers/domain/isOfferDisabled'
import {
  Events,
  OFFER_FORM_NAVIGATION_IN,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'
import { OfferBreadcrumbStep } from 'new_components/OfferBreadcrumb'

import EditStocksCell from './Cells/EditStocksCell'
import OfferInstitutionCell from './Cells/OfferInstitutionCell'
import OfferNameCell from './Cells/OfferNameCell'
import OfferRemainingStockCell from './Cells/OfferRemainingStockCell'
import OfferStatusCell from './Cells/OfferStatusCell'
import OfferVenueCell from './Cells/OfferVenueCell'
import ThumbCell from './Cells/ThumbCell'

export type OfferItemProps = {
  disabled?: boolean
  isSelected?: boolean
  offer: Offer
  selectOffer: (offerId: string, selected: boolean, isTemplate: boolean) => void
  audience: Audience
}

const OfferItem = ({
  disabled = false,
  offer,
  isSelected = false,
  selectOffer,
  audience,
}: OfferItemProps) => {
  const { venue, id, isEducational, isShowcase } = offer
  const { logEvent } = useAnalytics()
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')
  const editionOfferLink = useOfferEditionURL(
    isEducational,
    id,
    isOfferFormV3,
    !!isShowcase
  )
  const editionStockLink = useOfferStockEditionURL(
    isEducational,
    id,
    !!isShowcase
  )

  function handleOnChangeSelected() {
    selectOffer(offer.id, !isSelected, !!isShowcase)
  }

  const isOfferEditable = offer ? offer.isEditable : null
  const isOfferInactiveOrExpiredOrDisabled =
    !offer.isActive ||
    offer.hasBookingLimitDatetimesPassed ||
    isOfferDisabled(offer.status)

  return (
    <tr
      className={`offer-item ${
        isOfferInactiveOrExpiredOrDisabled ? 'inactive' : ''
      } offer-row`}
    >
      <td className="select-column">
        <input
          checked={isSelected}
          className="select-offer-checkbox"
          data-testid={`select-offer-${offer.id}`}
          disabled={disabled || isOfferDisabled(offer.status)}
          id={`select-offer-${offer.id}`}
          onChange={handleOnChangeSelected}
          type="checkbox"
        />
      </td>
      {audience === Audience.INDIVIDUAL && (
        <ThumbCell offer={offer} editionOfferLink={editionOfferLink} />
      )}
      <OfferNameCell offer={offer} editionOfferLink={editionOfferLink} />
      <OfferVenueCell venue={venue} />
      {audience === Audience.INDIVIDUAL ? (
        <OfferRemainingStockCell stocks={offer.stocks} />
      ) : (
        <OfferInstitutionCell
          educationalInstitution={offer.educationalInstitution}
        />
      )}
      <OfferStatusCell status={offer.status} />
      <EditStocksCell editionStockLink={editionStockLink} />
      <td className="edit-column">
        {isOfferEditable && (
          <Link
            className="secondary-link"
            onClick={() =>
              logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
                from: OFFER_FORM_NAVIGATION_IN.OFFERS,
                to: OfferBreadcrumbStep.SUMMARY,
                used: OFFER_FORM_NAVIGATION_MEDIUM.OFFERS_PEN,
                isEdition: true,
              })
            }
            to={editionOfferLink}
          >
            <Icon alt={`${offer.name} - éditer l'offre`} svg="ico-pen" />
          </Link>
        )}
      </td>
    </tr>
  )
}

export default OfferItem
