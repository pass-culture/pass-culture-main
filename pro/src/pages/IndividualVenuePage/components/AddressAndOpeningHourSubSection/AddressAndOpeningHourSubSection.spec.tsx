import { render, screen } from '@testing-library/react'

import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'

import { AddressAndOpeningHourSubSection } from './AddressAndOpeningHourSubSection'

const location = makeGetVenueResponseModel({
  id: 1,
  location: {
    ...makeGetVenueResponseModel({ id: 1 }).location,
    street: '1 rue de Paris',
    postalCode: '75001',
    city: 'Paris',
  },
}).location

describe('AddressAndOpeningHourSubSection', () => {
  it('should display the formatted address', () => {
    render(
      <AddressAndOpeningHourSubSection address={location} openingHours={null} />
    )

    expect(
      screen.getByText('Adresse : 1 rue de Paris, 75001 Paris')
    ).toBeInTheDocument()
  })

  it('should render the opening hours', () => {
    render(
      <AddressAndOpeningHourSubSection
        address={location}
        openingHours={{ MONDAY: [['09:00', '12:00']] }}
      />
    )

    expect(screen.getByText(/Lundi/)).toBeInTheDocument()
  })
})
