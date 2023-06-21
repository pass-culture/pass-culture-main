import './OfferSummary.scss'

import React from 'react'

import { OfferAddressType } from 'apiClient/adage'
import { ReactComponent as DateIcon } from 'icons/ico-date.svg'
import { ReactComponent as SubcategoryIcon } from 'icons/ico-subcategory.svg'
import { ReactComponent as LocationIcon } from 'icons/location.svg'
import buildingStrokeIcon from 'icons/stroke-building.svg'
import strokeEuro from 'icons/stroke-euro.svg'
import strokeUserIcon from 'icons/stroke-user.svg'
import {
  HydratedCollectiveOffer,
  HydratedCollectiveOfferTemplate,
} from 'pages/AdageIframe/app/types/offers'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { toISOStringWithoutMilliseconds } from 'utils/date'
import { formatLocalTimeDateString } from 'utils/timezone'

const extractDepartmentCode = (venuePostalCode: string): string => {
  const departmentNumberBase: number = parseInt(venuePostalCode.slice(0, 2))
  if (departmentNumberBase > 95) {
    return venuePostalCode.slice(0, 3)
  } else {
    return venuePostalCode.slice(0, 2)
  }
}

const getLocalBeginningDatetime = (
  beginningDatetime: string,
  venuePostalCode: string | null | undefined
): string => {
  if (!venuePostalCode) {
    return ''
  }

  const departmentCode = extractDepartmentCode(venuePostalCode)
  const stockBeginningDate = new Date(beginningDatetime)
  const stockBeginningDateISOString =
    toISOStringWithoutMilliseconds(stockBeginningDate)
  const stockLocalBeginningDate = formatLocalTimeDateString(
    stockBeginningDateISOString,
    departmentCode,
    'dd/MM/yyyy à HH:mm'
  )

  return stockLocalBeginningDate
}

const OfferSummary = ({
  offer,
}: {
  offer: HydratedCollectiveOffer | HydratedCollectiveOfferTemplate
}): JSX.Element => {
  const { subcategoryLabel, venue, offerVenue, students } = offer
  const { beginningDatetime, numberOfTickets, price } = offer.isTemplate
    ? {
        beginningDatetime: undefined,
        numberOfTickets: undefined,
        price: undefined,
      }
    : offer.stock

  let offerVenueLabel = `${venue.postalCode}, ${venue.city}`

  if (offerVenue) {
    if (offerVenue.addressType === OfferAddressType.OTHER) {
      offerVenueLabel = offerVenue.otherAddress
    } else if (offerVenue.addressType === OfferAddressType.SCHOOL) {
      offerVenueLabel = "Dans l'établissement scolaire"
    }
  }

  const studentsLabel = students
    ? students?.length > 1
      ? 'Multi niveaux'
      : students[0]
    : ''

  const getFormattedPrice = (price?: number) => {
    if (price === undefined || price === null) {
      return undefined
    }

    return price > 0
      ? new Intl.NumberFormat('fr-FR', {
          style: 'currency',
          currency: 'EUR',
        }).format(price / 100)
      : 'Gratuit'
  }

  const formattedPrice = getFormattedPrice(price)

  return (
    <div>
      <dl className="offer-summary">
        <div className="offer-summary-item">
          <dt>
            {/* TODO : add alt when changing to SvgIcon */}
            <SubcategoryIcon className="offer-summary-item-icon" />
          </dt>
          <dd>{subcategoryLabel}</dd>
        </div>
        <div className="offer-summary-item">
          <dt>
            {/* TODO : add alt when changing to SvgIcon */}
            <LocationIcon className="offer-summary-item-icon" />
          </dt>
          <dl>{offerVenueLabel}</dl>
        </div>
      </dl>
      <dl className="offer-summary">
        {beginningDatetime && (
          <div className="offer-summary-item">
            <dt>
              {/* TODO : add alt when changing to SvgIcon */}
              <DateIcon className="offer-summary-item-icon" />
            </dt>
            <dd>
              {getLocalBeginningDatetime(beginningDatetime, venue.postalCode)}
            </dd>
          </div>
        )}
        {numberOfTickets && (
          <div className="offer-summary-item">
            <dt>
              <SvgIcon
                src={strokeUserIcon}
                alt="Nombre de places"
                className="offer-summary-item-icon"
              />
            </dt>
            <dd>Jusqu’à {numberOfTickets} places</dd>
          </div>
        )}
        {formattedPrice && (
          <div className="offer-summary-item">
            <dt>
              <SvgIcon
                src={strokeEuro}
                alt="Prix"
                className="offer-summary-item-icon"
              />
            </dt>
            <dd>{formattedPrice}</dd>
          </div>
        )}
        {studentsLabel && (
          <div className="offer-summary-item">
            <dt>
              <SvgIcon
                src={buildingStrokeIcon}
                alt="Niveau scolaire"
                className="offer-summary-item-icon"
              />
            </dt>
            <dd>{studentsLabel}</dd>
          </div>
        )}
      </dl>
    </div>
  )
}

export default OfferSummary
