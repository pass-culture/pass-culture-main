import { axe } from 'vitest-axe'

import { defaultGetVenue } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { AccesLibreSection, AccesLibreSectionProps } from '../AccesLibreSection'

const renderAccesLibreSection = (props: Partial<AccesLibreSectionProps> = {}) =>
  renderWithProviders(<AccesLibreSection venue={defaultGetVenue} {...props} />)

describe('AccesLibreSection', () => {
  it('should pass axe accessibility tests', async () => {
    const { container } = renderAccesLibreSection({
      venue: {
        ...defaultGetVenue,
        externalAccessibilityData: {
          isAccessibleAudioDisability: true,
          isAccessibleMentalDisability: false,
          isAccessibleMotorDisability: true,
          isAccessibleVisualDisability: true,
          motorDisability: {
            facilities: 'Sanitaire adapté',
            exterior: 'Non renseigné',
            entrance: 'Non renseigné',
            parking: "Stationnement adapté dans l'établissement",
          },
          audioDisability: {
            deafAndHardOfHearing: 'boucle à induction magnétique fixe',
          },
          visualDisability: {
            soundBeacon: 'Non renseigné',
            audioDescription:
              'avec équipement permanent, casques et boîtiers disponibles à l’accueil',
          },
          mentalDisability: {
            trainedPersonnel: 'Personnel non sensibilisé / formé',
          },
        },
      },
    })

    expect(await axe(container)).toHaveNoViolations()
  })
})
