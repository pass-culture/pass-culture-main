import format from 'date-fns/format'
import React from 'react'

import { ReactComponent as BuildingIcon } from 'assets/building.svg'
import { ReactComponent as DateIcon } from 'assets/date.svg'
import { ReactComponent as EuroIcon } from 'assets/euro.svg'
import { ReactComponent as LocationIcon } from 'assets/location.svg'
import { ReactComponent as SubcategoryIcon } from 'assets/subcategory.svg'
import { ReactComponent as UserIcon } from 'assets/user.svg'
import { ADRESS_TYPE, OfferType } from 'utils/types'

import './OfferSummary.scss'

const OfferSummary = ({ offer }: { offer: OfferType }): JSX.Element => {
  const { subcategoryLabel, stocks, venue, extraData } = offer
  const { beginningDatetime, numberOfTickets, price } = stocks[0]

  let offerVenue = ''

  if (extraData?.offerVenue) {
    switch (extraData?.offerVenue.addressType) {
      case ADRESS_TYPE.OTHER:
        offerVenue = extraData.offerVenue.otherAddress
        break
      case ADRESS_TYPE.SCHOOL:
        offerVenue = "Dans l'établissement scolaire"
        break
      case ADRESS_TYPE.OFFERER_VENUE:
        offerVenue = `${venue.postalCode}, ${venue.city}`
        break
    }
  }

  const students = extraData?.students
    ? extraData.students?.length > 1
      ? 'Multi niveaux'
      : extraData.students[0]
    : ''

  return (
    <div>
      <ul className="offer-summary">
        <li className="offer-summary-item">
          <SubcategoryIcon className="offer-summary-item-icon" />
          {subcategoryLabel}
        </li>
        <li className="offer-summary-item">
          <DateIcon className="offer-summary-item-icon" />
          {format(new Date(beginningDatetime), 'dd/MM/yyyy à HH:mm')}
        </li>
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
        <li className="offer-summary-item">
          <EuroIcon className="offer-summary-item-icon" />
          {price}€
        </li>
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
