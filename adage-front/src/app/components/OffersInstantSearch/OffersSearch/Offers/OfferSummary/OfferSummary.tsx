import './OfferSummary.scss'

import React from 'react'

import { OfferAddressType } from 'apiClient'
import {
  HydratedCollectiveOffer,
  HydratedCollectiveOfferTemplate,
} from 'app/types/offers'
import { ReactComponent as BuildingIcon } from 'assets/building.svg'
import { ReactComponent as DateIcon } from 'assets/date.svg'
import { ReactComponent as EuroIcon } from 'assets/euro.svg'
import { ReactComponent as LocationIcon } from 'assets/location.svg'
import { ReactComponent as SubcategoryIcon } from 'assets/subcategory.svg'
import { ReactComponent as UserIcon } from 'assets/user.svg'
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
  if (!venuePostalCode) return ''

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
      <ul className="offer-summary">
        <li className="offer-summary-item">
          <SubcategoryIcon className="offer-summary-item-icon" />
          {subcategoryLabel}
        </li>
        {beginningDatetime && (
          <li className="offer-summary-item">
            <DateIcon className="offer-summary-item-icon" />
            {getLocalBeginningDatetime(beginningDatetime, venue.postalCode)}
          </li>
        )}
        <li className="offer-summary-item">
          <LocationIcon className="offer-summary-item-icon" />
          {offerVenueLabel}
        </li>
      </ul>
      <ul className="offer-summary">
        {numberOfTickets && (
          <li className="offer-summary-item">
            <UserIcon className="offer-summary-item-icon" />
            Jusqu’à {numberOfTickets} places
          </li>
        )}
        {formattedPrice && (
          <li className="offer-summary-item">
            <EuroIcon className="offer-summary-item-icon" />
            {formattedPrice}
          </li>
        )}
        {studentsLabel && (
          <li className="offer-summary-item">
            <BuildingIcon className="offer-summary-item-icon" />
            {studentsLabel}
          </li>
        )}
      </ul>
    </div>
  )
}

export default OfferSummary
