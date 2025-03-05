import { screen, render } from '@testing-library/react'

import { Hours, OpeningHoursReadOnly } from '../OpeningHoursReadOnly'

describe('OpeningHoursReadOnly', () => {
  it('should display each necessary days', () => {
    const openingHours = {
      MONDAY: [{ open: '14:00', close: '19:30' }],
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
    }

    render(
      <OpeningHoursReadOnly
        isOpenToPublicEnabled={false}
        isOpenToPublic={false}
        openingHours={openingHours}
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
    const openingHours = undefined
    render(
      <OpeningHoursReadOnly
        isOpenToPublicEnabled={false}
        isOpenToPublic={false}
        openingHours={openingHours}
      />
    )

    expect(
      screen.getByText(
        /Vous n’avez pas renseigné d’horaire d’ouverture. Votre établissement est indiqué comme fermé sur l’application./
      )
    ).toBeInTheDocument()
  })

  describe('when open to public feature is enabled', () => {
    it('should display a specific message when the venue is not open to public', () => {
      const openingHours = undefined
      render(
        <OpeningHoursReadOnly
          isOpenToPublicEnabled
          isOpenToPublic={false}
          openingHours={openingHours}
        />
      )

      expect(screen.getByText(/Accueil du public dans la structure : Non/)).toBeInTheDocument()
    })
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
