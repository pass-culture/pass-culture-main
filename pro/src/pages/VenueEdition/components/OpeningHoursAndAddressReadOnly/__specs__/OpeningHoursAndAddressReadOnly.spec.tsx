import { render, screen } from '@testing-library/react'

import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { getLocationResponseModel } from '@/commons/utils/factories/commonOffersApiFactories'

import { OpeningHoursAndAddressReadOnly } from '../OpeningHoursAndAddressReadOnly'
import { OpeningHoursReadOnlyHours } from '../OpeningHoursReadOnlyHours/OpeningHoursReadOnlyHours'

const MOCK_DATA = {
  venue: {
    ...defaultGetVenue,
    address: getLocationResponseModel(),
    openingHours: {
      MONDAY: [['08:00', '20:00']],
      TUESDAY: [
        ['10:00', '13:00'],
        ['14:00', '19:30'],
      ],
      WEDNESDAY: [
        ['10:00', '13:00'],
        ['14:00', '19:30'],
      ],
      THURSDAY: [
        ['10:00', '13:00'],
        ['14:00', '19:30'],
      ],
      FRIDAY: [
        ['10:00', '13:00'],
        ['14:00', '19:30'],
      ],
      SATURDAY: [
        ['10:00', '13:00'],
        ['14:00', '19:30'],
      ],
      SUNDAY: null,
    },
  },
}

describe('OpeningHoursAndAddressReadOnly', () => {
  it('should display each necessary days', () => {
    render(
      <OpeningHoursAndAddressReadOnly
        openingHours={MOCK_DATA.venue.openingHours}
      />
    )

    expect(screen.getByText(/Lundi/)).toBeInTheDocument()
    expect(screen.getByText(/Mardi/)).toBeInTheDocument()
    expect(screen.getByText(/Mercredi/)).toBeInTheDocument()
    expect(screen.getByText(/Jeudi/)).toBeInTheDocument()
    expect(screen.getByText(/Vendredi/)).toBeInTheDocument()
    expect(screen.getByText(/Samedi/)).toBeInTheDocument()
    expect(screen.queryByText(/Dimanche/)).not.toBeInTheDocument()
  })

  it('should display no opening hours !', () => {
    render(<OpeningHoursAndAddressReadOnly openingHours={undefined} />)

    expect(
      screen.getByText(
        "Horaires : Vos horaires d’ouverture ne sont pas affichées sur l'application car votre établissement est indiqué comme fermé tous les jours."
      )
    ).toBeInTheDocument()
  })

  it('should display the address', () => {
    render(
      <OpeningHoursAndAddressReadOnly
        openingHours={MOCK_DATA.venue.openingHours}
        address={MOCK_DATA.venue.address}
      />
    )

    const expectedText = `Adresse : ${MOCK_DATA.venue.address.street}, ${MOCK_DATA.venue.address.postalCode} ${MOCK_DATA.venue.address.city}`
    expect(screen.getByText(expectedText)).toBeInTheDocument()
  })

  it('should display opening hours when there are some', () => {
    render(
      <OpeningHoursAndAddressReadOnly
        openingHours={MOCK_DATA.venue.openingHours}
        address={MOCK_DATA.venue.address}
      />
    )

    const firstDay = MOCK_DATA.venue.openingHours.MONDAY
    expect(screen.getByText(/Lundi/)).toBeInTheDocument()
    expect(screen.getByText(firstDay[0][0])).toBeInTheDocument()
    expect(screen.getByText(firstDay[0][1])).toBeInTheDocument()
  })

  it('should display an default message when opening hours are not set', () => {
    render(
      <OpeningHoursAndAddressReadOnly
        openingHours={null}
        address={MOCK_DATA.venue.address}
      />
    )

    expect(
      screen.getByText(
        "Horaires : Vos horaires d’ouverture ne sont pas affichées sur l'application car votre établissement est indiqué comme fermé tous les jours."
      )
    ).toBeInTheDocument()
  })

  it('should display a default message when opening hours are set but empty', () => {
    render(
      <OpeningHoursAndAddressReadOnly
        openingHours={{}}
        address={MOCK_DATA.venue.address}
      />
    )

    expect(
      screen.getByText(
        "Horaires : Vos horaires d’ouverture ne sont pas affichées sur l'application car votre établissement est indiqué comme fermé tous les jours."
      )
    ).toBeInTheDocument()
  })
})

describe('DayAndHours', () => {
  it('should display each hours and day when half a day', () => {
    const openingHours = [['14:00', '19:30']]

    render(<OpeningHoursReadOnlyHours openingHoursForDay={openingHours} />)

    expect(screen.getByText('14:00')).toBeInTheDocument()
    expect(screen.getByText('19:30')).toBeInTheDocument()
    expect(screen.queryByText(/et de/)).not.toBeInTheDocument()
  })

  it('should display each hours and day when the whole day', () => {
    const openingHours = [
      ['10:00', '12:30'],
      ['14:00', '19:30'],
    ]

    render(<OpeningHoursReadOnlyHours openingHoursForDay={openingHours} />)

    expect(screen.getByText('10:00')).toBeInTheDocument()
    expect(screen.getByText('12:30')).toBeInTheDocument()
    expect(screen.getByText('14:00')).toBeInTheDocument()
    expect(screen.getByText('19:30')).toBeInTheDocument()
    expect(screen.getByText(/et de/)).toBeInTheDocument()
  })
})
