import { screen } from '@testing-library/react'
import React from 'react'

import { CollectiveOfferOfferVenue, OfferAddressType } from 'apiClient/adage'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferVenue from '../OfferVenue'

const renderOfferVenue = (offerVenue: CollectiveOfferOfferVenue) => {
  return renderWithProviders(<OfferVenue offerVenue={offerVenue} />)
}

describe('OfferVenue', () => {
  const defaultOfferVenue = {
    addressType: OfferAddressType.OFFERER_VENUE,
    venueId: 1,
    name: 'Nom juridique',
    publicName: 'Mon petit cinema',
    otherAddress: '',
  }

  it('should display public name(if valued) of the venue when addressType is OFFERER_VENUE', () => {
    renderOfferVenue(defaultOfferVenue)

    expect(screen.getByText('Mon petit cinema')).toBeInTheDocument()
  })

  it('should display name (if public name not valued) of the venue when addressType is OFFERER_VENUE', () => {
    renderOfferVenue({
      ...defaultOfferVenue,
      publicName: '',
    })

    expect(screen.getByText('Nom juridique')).toBeInTheDocument()
  })

  it('should display other address when addressType is OTHER', () => {
    renderOfferVenue({
      ...defaultOfferVenue,
      addressType: OfferAddressType.OTHER,
      otherAddress: 'Mon autre adresse',
    })

    expect(screen.getByText('Mon autre adresse')).toBeInTheDocument()
  })

  it('should display in school message when addressType is IN_SCHOOL', () => {
    renderOfferVenue({
      ...defaultOfferVenue,
      addressType: OfferAddressType.SCHOOL,
    })

    expect(
      screen.getByText('Dans l’établissement scolaire')
    ).toBeInTheDocument()
  })
})
