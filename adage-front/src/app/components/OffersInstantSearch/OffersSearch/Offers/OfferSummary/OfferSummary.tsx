import React from 'react'

import { ReactComponent as BuildingIcon } from 'assets/building.svg'
import { ReactComponent as DateIcon } from 'assets/date.svg'
import { ReactComponent as EuroIcon } from 'assets/euro.svg'
import { ReactComponent as LocationIcon } from 'assets/location.svg'
import { ReactComponent as SubcategoryIcon } from 'assets/subcategory.svg'
import { ReactComponent as UserIcon } from 'assets/user.svg'
import { toISOStringWithoutMilliseconds } from 'utils/date'
import { formatLocalTimeDateString } from 'utils/timezone'
import { ADRESS_TYPE, OfferType } from 'utils/types'

import './OfferSummary.scss'

const extractDepartmentCode = (venuePostalCode: string): string => {
  const departmentNumberBase: number = parseInt(venuePostalCode.slice(0, 2))
  if (departmentNumberBase > 95) {
    return venuePostalCode.slice(0, 3)
  } else {
    return venuePostalCode.slice(0, 2)
  }
}

const getLocalBeginningDatetime = (
  beginningDatetime: Date,
  venuePostalCode: string
): string => {
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

const OfferSummary = ({ offer }: { offer: OfferType }): JSX.Element => {
  const { subcategoryLabel, stocks, venue, extraData } = offer
  const { beginningDatetime, numberOfTickets, price } = extraData?.isShowcase
    ? {
        beginningDatetime: undefined,
        numberOfTickets: undefined,
        price: undefined,
      }
    : stocks[0]

  let offerVenue = `${venue.postalCode}, ${venue.city}`

  if (extraData?.offerVenue) {
    if (extraData?.offerVenue.addressType === ADRESS_TYPE.OTHER) {
      offerVenue = extraData.offerVenue.otherAddress
    } else if (extraData?.offerVenue.addressType === ADRESS_TYPE.SCHOOL) {
      offerVenue = "Dans l'établissement scolaire"
    }
  }

  const students = extraData?.students
    ? extraData.students?.length > 1
      ? 'Multi niveaux'
      : extraData.students[0]
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
          {offerVenue}
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
        {students && (
          <li className="offer-summary-item">
            <BuildingIcon className="offer-summary-item-icon" />
            {students}
          </li>
        )}
      </ul>
    </div>
  )
}

export default OfferSummary
