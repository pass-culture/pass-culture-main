import { screen, render } from '@testing-library/react'

import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'
import { getAddressResponseIsLinkedToVenueModelFactory } from 'commons/utils/factories/commonOffersApiFactories'

import { Hours, OpeningHoursReadOnly } from '../OpeningHoursReadOnly'

const MOCK_DATA = {
  venue: {
    ...defaultGetVenue,
    address: getAddressResponseIsLinkedToVenueModelFactory(),
    openingHours: {
      MONDAY: [{ open: '08:00', close: '20:00' }],
      TUESDAY: [
        { open: '10:00', close: '13:00' },
        { open: '14:00', close: '19:30' },
      ],
      WEDNESDAY: [
        { open: '10:00', close: '13:00' },
        { open: '14:00', close: '19:30' },
      ],
      THURSDAY: [
        { open: '10:00', close: '13:00' },
        { open: '14:00', close: '19:30' },
      ],
      FRIDAY: [
        { open: '10:00', close: '13:00' },
        { open: '14:00', close: '19:30' },
      ],
      SATURDAY: [
        { open: '10:00', close: '13:00' },
        { open: '14:00', close: '19:30' },
      ],
      SUNDAY: null,
    },
  },
}

describe('OpeningHoursReadOnly', () => {
  it('should display each necessary days', () => {
    render(<OpeningHoursReadOnly openingHours={MOCK_DATA.venue.openingHours} />)

    expect(screen.getByText(/Lundi/)).toBeInTheDocument()
    expect(screen.getByText(/Mardi/)).toBeInTheDocument()
    expect(screen.getByText(/Mercredi/)).toBeInTheDocument()
    expect(screen.getByText(/Jeudi/)).toBeInTheDocument()
    expect(screen.getByText(/Vendredi/)).toBeInTheDocument()
    expect(screen.getByText(/Samedi/)).toBeInTheDocument()
    expect(screen.queryByText(/Dimanche/)).not.toBeInTheDocument()
  })

  it('should display no opening hours !', () => {
    render(<OpeningHoursReadOnly openingHours={undefined} />)

    expect(
      screen.getByText(
        /Vous n’avez pas renseigné d’horaire d’ouverture. Votre établissement est indiqué comme fermé sur l’application./
      )
    ).toBeInTheDocument()
  })

  it('should display the address', () => {
    render(
      <OpeningHoursReadOnly
        openingHours={MOCK_DATA.venue.openingHours}
        address={MOCK_DATA.venue.address}
      />
    )

    const expectedText = `Adresse : ${MOCK_DATA.venue.address.street}, ${MOCK_DATA.venue.address.postalCode} ${MOCK_DATA.venue.address.city}`
    expect(screen.getByText(expectedText)).toBeInTheDocument()
  })

  it('should display opening hours when there are some', () => {
    render(
      <OpeningHoursReadOnly
        openingHours={MOCK_DATA.venue.openingHours}
        address={MOCK_DATA.venue.address}
      />
    )

    const firstDay = MOCK_DATA.venue.openingHours.MONDAY
    expect(screen.getByText(/Lundi/)).toBeInTheDocument()
    expect(screen.getByText(firstDay[0].open)).toBeInTheDocument()
    expect(screen.getByText(firstDay[0].close)).toBeInTheDocument()
  })

  it('should display an empty state message when opening hours are not set', () => {
    render(
      <OpeningHoursReadOnly
        openingHours={null}
        address={MOCK_DATA.venue.address}
      />
    )

    expect(screen.getByText(/Horaires : Non renseigné/)).toBeInTheDocument()
  })

  it('should display a closed state message when opening hours are set but empty', () => {
    render(
      <OpeningHoursReadOnly
        openingHours={{}}
        address={MOCK_DATA.venue.address}
      />
    )

    expect(
      screen.getByText(
        /Horaires : Vous n’avez pas renseigné d’horaire d’ouverture. Votre établissement est indiqué comme fermé sur l’application./
      )
    ).toBeInTheDocument()
  })
})

describe('DayAndHours', () => {
  it('should display each hours and day when half a day', () => {
    const openingHours = [{ open: '14:00', close: '19:30' }]

    render(<Hours hours={openingHours} />)

    expect(screen.getByText('14:00')).toBeInTheDocument()
    expect(screen.getByText('19:30')).toBeInTheDocument()
    expect(screen.queryByText(/et de/)).not.toBeInTheDocument()
  })

  it('should display each hours and day when the whole day', () => {
    const openingHours = [
      { open: '10:00', close: '12:30' },
      { open: '14:00', close: '19:30' },
    ]

    render(<Hours hours={openingHours} />)

    expect(screen.getByText('10:00')).toBeInTheDocument()
    expect(screen.getByText('12:30')).toBeInTheDocument()
    expect(screen.getByText('14:00')).toBeInTheDocument()
    expect(screen.getByText('19:30')).toBeInTheDocument()
    expect(screen.getByText(/et de/)).toBeInTheDocument()
  })
})
