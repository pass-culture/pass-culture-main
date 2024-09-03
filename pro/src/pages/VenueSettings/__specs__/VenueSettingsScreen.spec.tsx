import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { VenueTypeResponseModel } from 'apiClient/v1'
import { defaultGetVenue } from 'utils/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  defaultVenueProvider,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { VenueSettingsScreen } from '../VenueSettingsScreen'

const venueTypes: VenueTypeResponseModel[] = [
  { id: 'ARTISTIC_COURSE', label: 'Cours et pratique artistiques' },
  { id: 'SCIENTIFIC_CULTURE', label: 'Culture scientifique' },
]

const renderForm = async () => {
  renderWithProviders(
    <VenueSettingsScreen
      offerer={{
        ...defaultGetOffererResponseModel,
        id: 12,
        siren: '881457238',
      }}
      venueTypes={venueTypes}
      venueLabels={[
        { label: 'Lieu de spectacle', value: 'show' },
        { label: 'Lieu de pratique', value: 'practice' },
      ]}
      venueProviders={[
        defaultVenueProvider,
        {
          id: 2,
          isActive: true,
          isFromAllocineProvider: true,
          lastSyncDate: undefined,
          venueId: 2,
          dateCreated: '2021-08-15T00:00:00Z',
          venueIdAtOfferProvider: 'allocine_id_1',
          provider: {
            name: 'Allociné',
            id: 13,
            hasOffererProvider: false,
            isActive: true,
          },
          quantity: 0,
          isDuo: true,
          price: 0,
        },
      ]}
      venue={defaultGetVenue}
      initialValues={{
        addressAutocomplete: '123 Rue Principale, Ville Exemple',
        banId: '12345',
        bookingEmail: 'contact@lieuexemple.com',
        city: 'Ville Exemple',
        comment: 'Un lieu populaire pour les concerts et les événements',
        isWithdrawalAppliedOnAllOffers: true,
        latitude: 48.8566,
        longitude: 2.3522,
        name: 'Lieu Exemple',
        postalCode: '75001',
        publicName: 'Lieu Exemple Public',
        'search-addressAutocomplete': '123 Rue Principale, Ville Exemple',
        siret: '12345678901234',
        street: '123 Rue Principale',
        venueSiret: 12345678901234,
        venueLabel: 'Salle de Concert',
        venueType: 'Théâtre',
        withdrawalDetails:
          "Les retraits sont autorisés jusqu'à 24 heures avant l'événement.",
      }}
    />,
    {
      user: sharedCurrentUserFactory(),
    }
  )

  await waitFor(() => {
    screen.getByText('Paramètres généraux')
  })
}

describe('VenueSettingsScreen', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getProvidersByVenue').mockResolvedValue([
      {
        name: 'Ciné Office',
        id: 12,
        hasOffererProvider: false,
        isActive: true,
      },
      {
        name: 'Allociné',
        id: 13,
        hasOffererProvider: false,
        isActive: true,
      },
      {
        name: 'Ticket Buster',
        id: 14,
        hasOffererProvider: true,
        isActive: true,
      },
    ])
  })

  it('should display the route leaving guard when leaving without saving', async () => {
    await renderForm()

    await userEvent.type(screen.getByLabelText('Nom public'), 'test')
    await userEvent.click(screen.getByText('Annuler'))

    expect(
      screen.getByText('Les informations non enregistrées seront perdues')
    ).toBeInTheDocument()
  })

  it('should display the venue provider cards & add provider button', async () => {
    await renderForm()

    const cineOfficeCard = screen.getByText('Ciné Office')
    const allocineCard = screen.getByText('Allociné')
    const addProviderButton = screen.getByRole('button', {
      name: 'Sélectionner un logiciel',
    })

    expect(cineOfficeCard).toBeInTheDocument()
    expect(allocineCard).toBeInTheDocument()
    expect(addProviderButton).toBeInTheDocument()
  })
})
