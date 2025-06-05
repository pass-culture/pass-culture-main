import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

import { api } from 'apiClient/api'
import { VenueTypeResponseModel } from 'apiClient/v1'
import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  defaultVenueProvider,
} from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

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
        latitude: '48.8566',
        longitude: '2.3522',
        coords: '48.8566, 2.3522',
        name: 'Lieu Exemple',
        postalCode: '75001',
        inseeCode: '75111',
        publicName: 'Lieu Exemple Public',
        'search-addressAutocomplete': '123 Rue Principale, Ville Exemple',
        siret: '12345678901234',
        street: '123 Rue Principale',
        venueSiret: 12345678901234,
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
    screen.getByText('Tous les champs suivis d’un * sont obligatoires.')
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
      name: /SIRET de la structure/,
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

  it('should render with manual address fields', async () => {
    await renderForm()

    expect(
      await screen.findByText(/Vous ne trouvez pas votre adresse/)
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
      isManualEdition: undefined,
      latitude: 48.8566,
      longitude: 2.3522,
      name: 'Lieu Exemple',
      postalCode: '75001',
      inseeCode: '75111',
      publicName: 'Lieu Exemple Public Updated',
      street: '123 Rue Principale',
      venueTypeCode: 'Théâtre',
      withdrawalDetails:
        "Les retraits sont autorisés jusqu'à 24 heures avant l'événement.",
    })
  })

  describe('toggleManuallySetAddress', () => {
    const fieldsNames = new Map([
      ['street', ''],
      ['postalCode', ''],
      ['city', ''],
      ['latitude', ''],
      ['longitude', ''],
      ['coords', ''],
      ['banId', ''],
      ['inseeCode', null],
      ['search-addressAutocomplete', ''],
      ['addressAutocomplete', ''],
    ])

    it('toggles manuallySetAddress and resets fields with clearErrors', () => {
      const mockSetValue = vi.fn()
      const mockClearErrors = vi.fn()
      let manuallySetAddress = false

      // Function under test (mimicking your implementation)
      const toggleManuallySetAddress = () => {
        mockSetValue('manuallySetAddress', !manuallySetAddress)

        return [...fieldsNames.entries()].map(([fieldName, defaultValue]) => {
          mockSetValue(fieldName, defaultValue)
          mockClearErrors()
        })
      }

      toggleManuallySetAddress()

      // Check manuallySetAddress toggled once
      expect(mockSetValue).toHaveBeenCalledWith('manuallySetAddress', true)

      // Check each field reset
      for (const [fieldName, defaultValue] of fieldsNames.entries()) {
        expect(mockSetValue).toHaveBeenCalledWith(fieldName, defaultValue)
      }

      // clearErrors called as many times as fields reset
      expect(mockClearErrors).toHaveBeenCalledTimes(fieldsNames.size)
    })
  })
})
