import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { VenueTypeResponseModel } from 'apiClient/v1'
import { defaultGetVenue } from 'utils/collectiveApiFactories'
import { defaultGetOffererResponseModel } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { VenueSettingsFormScreen } from '../VenueSettingsScreen'

const venueTypes: VenueTypeResponseModel[] = [
  { id: 'ARTISTIC_COURSE', label: 'Cours et pratique artistiques' },
  { id: 'SCIENTIFIC_CULTURE', label: 'Culture scientifique' },
]

const renderForm = () => {
  renderWithProviders(
    <VenueSettingsFormScreen
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
      venueProviders={[]}
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
}

describe('VenueSettingsFormScreen', () => {
  it('should display the route leaving guard when leaving without saving', async () => {
    renderForm()

    await userEvent.type(screen.getByLabelText('Nom public'), 'test')
    await userEvent.click(screen.getByText('Annuler'))

    await waitFor(() => {
      expect(
        screen.getByText('Les informations non enregistrées seront perdues')
      ).toBeInTheDocument()
    })
  })
})
