import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from 'apiClient/api'
import { VenueTypeResponseModel } from 'apiClient/v1'
import { defaultGetVenue } from 'utils/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  defaultVenueProvider,
} from 'utils/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { VenueSettingsScreen } from '../VenueSettingsScreen'

const venueTypes: VenueTypeResponseModel[] = [
  { id: 'ARTISTIC_COURSE', label: 'Cours et pratique artistiques' },
  { id: 'SCIENTIFIC_CULTURE', label: 'Culture scientifique' },
]

const renderForm = async (options?: RenderWithProvidersOptions) => {
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
        latitude: '48.8566',
        longitude: '2.3522',
        coords: '48.8566, 2.3522',
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
      ...options,
    }
  )

  await waitFor(() => {
    screen.getByText('Paramètres généraux')
  })
}

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))
Element.prototype.scrollIntoView = vi.fn()

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

  it('should render the venue settings form with venue data', async () => {
    await renderForm()

    const siretField = await screen.findByRole('textbox', {
      name: /SIRET du lieu/,
    })
    const nameField = await screen.findByRole('textbox', {
      name: /Raison sociale/,
    })
    const publicNameField = await screen.findByRole('textbox', {
      name: /Nom public/,
    })
    const addressField = await screen.findByRole('combobox', {
      name: /Adresse postale/,
    })
    const withdrawalDetailsField = await screen.findByRole('textbox', {
      name: /Informations de retrait/,
    })
    const emailField = await screen.findByRole('textbox', {
      name: /Adresse email/,
    })

    expect(siretField).toBeInTheDocument()
    expect(nameField).toBeInTheDocument()
    expect(publicNameField).toBeInTheDocument()
    expect(addressField).toBeInTheDocument()
    expect(withdrawalDetailsField).toBeInTheDocument()
    expect(emailField).toBeInTheDocument()

    expect(siretField).toHaveValue('12345678901234')
    expect(nameField).toHaveValue('Lieu Exemple')
    expect(publicNameField).toHaveValue('Lieu Exemple Public')
    expect(addressField).toHaveValue('123 Rue Principale, Ville Exemple')
    expect(withdrawalDetailsField).toHaveValue(
      "Les retraits sont autorisés jusqu'à 24 heures avant l'événement."
    )
    expect(emailField).toHaveValue('contact@lieuexemple.com')
  })

  it('should display the withdrawal confirm dialog when submitting with the box checked', async () => {
    await renderForm()

    await userEvent.type(
      screen.getByLabelText('Informations de retrait'),
      'Nouvelle infos de retrait'
    )
    await userEvent.click(screen.getByText('Enregistrer'))

    expect(
      screen.getByText(
        'Souhaitez-vous prévenir les bénéficiaires de la modification des modalités de retrait ?'
      )
    ).toBeInTheDocument()
  })

  it('should render with manual address fields when WIP_ENABLE_OFFER_ADDRESS feature is enabled', async () => {
    await renderForm({ features: ['WIP_ENABLE_OFFER_ADDRESS'] })

    expect(
      await screen.findByText(/Vous ne trouvez pas votre adresse/)
    ).toBeInTheDocument()
  })

  it('should display the address change modal when updating venue address', async () => {
    await renderForm({ features: ['WIP_ENABLE_OFFER_ADDRESS'] })

    await userEvent.click(
      screen.getByRole('button', { name: /Vous ne trouvez pas votre adresse/ })
    )

    const cityField = screen.getByRole('textbox', { name: /Ville/ })
    const streetField = screen.getByRole('textbox', { name: /Adresse postale/ })
    const postalCodeField = screen.getByRole('textbox', { name: /Code postal/ })
    const coordsField = screen.getByRole('textbox', { name: /Coordonnées GPS/ })

    await userEvent.type(cityField, 'Changed city')
    await userEvent.type(streetField, 'Changed street')
    await userEvent.type(postalCodeField, '00000')
    await userEvent.type(coordsField, '49.999, 3.3333')

    await userEvent.click(screen.getByText('Enregistrer'))

    expect(
      await screen.findByText(
        /Ce changement d'adresse ne va pas s'impacter sur vos offres/
      )
    ).toBeInTheDocument()
  })

  it('should submit the form with valid payload', async () => {
    const apiPatchVenue = vi.spyOn(api, 'editVenue')

    await renderForm()

    const publicNameField = await screen.findByRole('textbox', {
      name: /Nom public/,
    })

    await userEvent.clear(publicNameField)
    await userEvent.type(publicNameField, 'Lieu Exemple Public Updated')
    await userEvent.click(screen.getByText('Enregistrer'))

    expect(apiPatchVenue).toHaveBeenCalledWith(1, {
      banId: '12345',
      bookingEmail: 'contact@lieuexemple.com',
      city: 'Ville Exemple',
      comment: 'Un lieu populaire pour les concerts et les événements',
      isEmailAppliedOnAllOffers: true,
      isManualEdition: undefined,
      isWithdrawalAppliedOnAllOffers: true,
      latitude: '48.8566',
      longitude: '2.3522',
      name: 'Lieu Exemple',
      postalCode: '75001',
      publicName: 'Lieu Exemple Public Updated',
      shouldSendMail: false,
      street: '123 Rue Principale',
      venueLabelId: NaN,
      venueTypeCode: 'Théâtre',
      withdrawalDetails:
        "Les retraits sont autorisés jusqu'à 24 heures avant l'événement.",
    })
  })
})
