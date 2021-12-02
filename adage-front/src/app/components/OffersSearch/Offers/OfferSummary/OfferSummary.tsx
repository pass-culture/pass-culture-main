import format from 'date-fns/format'
import React from 'react'

import { ReactComponent as DateIcon } from "assets/date.svg"
import { ReactComponent as EuroIcon } from "assets/euro.svg"
import { ReactComponent as LocationIcon } from "assets/location.svg"
import { ReactComponent as SubcategoryIcon } from "assets/subcategory.svg"
import { OfferType } from 'utils/types'

import './OfferSummary.scss'

const OfferSummary = ({offer}: {offer: OfferType}): JSX.Element => (
  <>
    <ul className="offer-summary">
      <li className="offer-summary-item">
        <SubcategoryIcon className="offer-summary-item-icon" />
        {offer.subcategoryLabel}
      </li>
      <li className="offer-summary-item">
        <DateIcon className="offer-summary-item-icon" />
        {format(new Date(offer.stocks[0].beginningDatetime), 'dd/MM/yyyy à HH:mm')}
      </li>
      <li className="offer-summary-item">
        <LocationIcon className="offer-summary-item-icon" />
        {offer.venue.publicName}
      </li>
    </ul>
    <ul className="offer-summary">
      <li className="offer-summary-item">
        <EuroIcon className="offer-summary-item-icon" />
        {offer.stocks[0].price}
        €
      </li>
    </ul>
  </>
)

export default OfferSummary