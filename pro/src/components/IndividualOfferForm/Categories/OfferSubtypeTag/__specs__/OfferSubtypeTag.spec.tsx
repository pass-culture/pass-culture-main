import { render } from '@testing-library/react'
import React from 'react'

import { INDIVIDUAL_OFFER_SUBTYPE } from 'core/Offers/constants'

import { OfferSubtypeTag } from '../OfferSubtypeTag'

describe('OfferSubtypeTag', () => {
  const cases = [
    INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT,
    INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT,
    INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD,
    INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD,
  ]
  it.each(cases)('should render without error for subtype %s', offerSubtype => {
    render(<OfferSubtypeTag offerSubtype={offerSubtype} />)
  })
})
