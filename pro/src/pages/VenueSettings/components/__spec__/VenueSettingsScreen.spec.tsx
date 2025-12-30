import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect } from 'vitest'

import * as apiAdresse from '@/apiClient/adresse/apiAdresse'
import { api } from '@/apiClient/api'
import { type GetVenueResponseModel, VenueTypeCode } from '@/apiClient/v1'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  defaultVenueProvider,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { structureDataBodyModelFactory } from '@/commons/utils/factories/userOfferersFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  VenueSettingsScreen,
  type VenueSettingsScreenProps,
} from '../VenueSettingsScreen'

const mockNavigate = vi.fn()
vi.mock('react-router', async () => {
  return {
    ...(await vi.importActual('react-router')),
    useNavigate: () => mockNavigate,
    default: vi.fn(),
  }
})

const firstVenueProvider = { ...defaultVenueProvider }
const secondVenueProvider = {
  id: 2,
  isActive: true,
  isFromAllocineProvider: true,
  lastSyncDate: null,
  venueId: 2,
  dateCreated: '2021-08-15T00:00:00Z',
  venueIdAtOfferProvider: 'allocine_id_1',
  provider: {
    name: 'Allociné',
    id: 13,
    hasOffererProvider: false,
    isActive: true,
    enabledForPro: true,
  },
  quantity: 0,
  isDuo: true,
  price: 0,
}

const defaultOfferer = {
  ...defaultGetOffererResponseModel,
  id: 12,
  siren: '123456789',
}

const defaultVenue: GetVenueResponseModel = {
  ...defaultGetVenue,
  name: 'Lieu de test',
  publicName: 'Lieu Exemple Public',
  location: {
    banId: '12345',
    id: 2,
    isVenueLocation: false,
    street: '123 Rue Principale',
    city: 'Ville Exemple',
    postalCode: '75001',
    inseeCode: '75111',
    isManualEdition: false,
    latitude: 48.8566,
    longitude: 2.3522,
  },
  venueType: { value: VenueTypeCode.CENTRE_CULTUREL, label: 'Centre culturel' },
  comment: 'Un lieu populaire pour les concerts et les événements',
  bookingEmail: 'contact@lieuexemple.com',
  withdrawalDetails:
    "Les retraits sont autorisés jusqu'à 24 heures avant l'événement.",
}

const mockAdressData = [
  {
    address: '10 Rue des lilas',
    city: 'Lyon',
    id: '1',
    latitude: 11.1,
    longitude: -11.1,
    label: '10 Rue des lilas 69002 Lyon',
    postalCode: '69002',
    inseeCode: '69002',
  },
]

const renderForm = async (
  props?: Partial<VenueSettingsScreenProps>,
  globalOptions?: RenderWithProvidersOptions
) => {
  renderWithProviders(
    <VenueSettingsScreen
      offerer={{
        ...defaultOfferer,
        ...(props?.offerer || {}),
      }}
      venueProviders={[firstVenueProvider, secondVenueProvider]}
      venue={{
        ...defaultVenue,
        ...(props?.venue || {}),
      }}
    />,
    {
      user: sharedCurrentUserFactory(),
      ...globalOptions,
    }
  )

  await waitFor(() => {
    screen.getByText('Les champs suivis d’un * sont obligatoires.')
  })
}

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(() => true),
}))
Element.prototype.scrollIntoView = vi.fn()

describe('VenueSettingsScreen', () => {
  beforeEach(() => {
    vi.spyOn(apiAdresse, 'getDataFromAddress').mockResolvedValue(mockAdressData)
    vi.spyOn(api, 'getProvidersByVenue').mockResolvedValue([
      {
        name: 'Ciné Office',
        id: 12,
        hasOffererProvider: false,
        isActive: true,
        enabledForPro: true,
      },
      {
        name: 'Allociné',
        id: 13,
        hasOffererProvider: false,
        isActive: true,
        enabledForPro: true,
      },
      {
        name: 'Ticket Buster',
        id: 14,
        hasOffererProvider: true,
        isActive: true,
        enabledForPro: true,
      },
    ])
  })

  describe('Route leaving guard', () => {
    it.each([
      { label: 'SIRET de la structure', ariaRole: 'textbox' },
      { label: 'Nom public', ariaRole: 'textbox' },
      { label: 'Informations de retrait', ariaRole: 'textbox' },
      { label: 'Adresse email', ariaRole: 'textbox' },
    ])('should display the route leaving guard when leaving without saving field "$label"', async (field: {
      label: string
      ariaRole: string
    }) => {
      await renderForm({
        venue: { ...defaultGetVenue, siret: '53912345600026' },
      })

      await userEvent.type(
        screen.getByRole(field.ariaRole, { name: new RegExp(field.label) }),
        '123' // Test value must be a number string so it doesn't breaks input types number validation (siret) in this test suite
      )
      await userEvent.click(screen.getByText('Annuler'))

      expect(
        screen.getByText('Les informations non enregistrées seront perdues')
      ).toBeInTheDocument()
    })

    it.each([
      { label: 'Adresse postale', ariaRole: 'textbox' },
      { label: 'Code postal', ariaRole: 'textbox' },
      { label: 'Ville', ariaRole: 'textbox' },
      { label: 'Coordonnées GPS', ariaRole: 'textbox' },
    ])('should display the route leaving guard when leaving without saving field "$label"', async (field: {
      label: string
      ariaRole: string
    }) => {
      await renderForm({
        venue: { ...defaultGetVenue, siret: '53912345600026' },
      })

      // We need to trigger manual address edition to show address fields
      await userEvent.click(
        screen.getByText('Vous ne trouvez pas votre adresse ?')
      )

      await userEvent.type(
        screen.getByRole(field.ariaRole, { name: new RegExp(field.label) }),
        'test'
      )
      await userEvent.click(screen.getByText('Annuler'))

      expect(
        screen.getByText('Les informations non enregistrées seront perdues')
      ).toBeInTheDocument()
    })
  })

  it('should redirect back to the previous page when clicking on back button', async () => {
    await renderForm()

    await userEvent.click(screen.getByText('Retour vers la page précédente'))

    expect(mockNavigate).toHaveBeenCalledExactlyOnceWith(-1)
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
    await renderForm({
      venue: {
        ...defaultVenue,
        siret: '123 456 789 01234',
      },
    })

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

    expect(siretField).toHaveValue('123 456 789 01234')
    expect(nameField).toHaveValue('Lieu de test')
    expect(publicNameField).toHaveValue('Lieu Exemple Public')
    expect(addressField).toHaveValue('123 Rue Principale 75001 Ville Exemple')
    expect(withdrawalDetailsField).toHaveValue(
      "Les retraits sont autorisés jusqu'à 24 heures avant l'événement."
    )
    expect(emailField).toHaveValue('contact@lieuexemple.com')
  })

  it('should submit the form with valid payload', async () => {
    const apiPatchVenue = vi
      .spyOn(api, 'editVenue')
      .mockResolvedValueOnce(defaultVenue)
    await renderForm({ venue: { ...defaultVenue, siret: '123 456 789 01234' } })

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
      comment: '',
      isManualEdition: false,
      latitude: 48.8566,
      longitude: 2.3522,
      name: 'Lieu de test',
      postalCode: '75001',
      inseeCode: '75111',
      publicName: 'Lieu Exemple Public Updated',
      street: '123 Rue Principale',
      siret: '12345678901234',
      withdrawalDetails:
        "Les retraits sont autorisés jusqu'à 24 heures avant l'événement.",
    })
  })

  it('should submit the form with valid payload for New Caledonia', async () => {
    const apiPatchVenue = vi
      .spyOn(api, 'editVenue')
      .mockResolvedValueOnce(defaultVenue)

    await renderForm({
      offerer: { ...defaultOfferer, siren: 'NC1234567' },
      venue: {
        ...defaultVenue,
        isCaledonian: true,
        siret: 'NC1234567890XX',
      },
    })

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
      comment: '',
      isManualEdition: false,
      latitude: 48.8566,
      longitude: 2.3522,
      name: 'Lieu de test',
      postalCode: '75001',
      inseeCode: '75111',
      publicName: 'Lieu Exemple Public Updated',
      street: '123 Rue Principale',
      siret: 'NC1234567890XX',
      withdrawalDetails:
        "Les retraits sont autorisés jusqu'à 24 heures avant l'événement.",
    })
  })

  it('should not change name if siret is not diffusible', async () => {
    vi.spyOn(api, 'getStructureData').mockResolvedValue({
      ...structureDataBodyModelFactory(),
      name: "Le Siret n'est pas diffusible",
      isDiffusible: false,
    })

    await renderForm({
      venue: {
        ...defaultVenue,
        siret: '123 456 789 01234',
      },
    })

    const siretField = await screen.findByRole('textbox', {
      name: /SIRET de la structure/,
    })
    const nameField = await screen.findByRole('textbox', {
      name: /Raison sociale/,
    })

    await userEvent.clear(siretField)
    await userEvent.type(siretField, '12345678901234')
    await userEvent.tab()
    expect(nameField).not.toHaveValue("Le Siret n'est pas diffusible")
    expect(nameField).toHaveValue('Lieu de test')
  })

  it('toggles manuallySetAddress and resets fields with clearErrors', async () => {
    await renderForm({
      venue: {
        ...defaultVenue,
        siret: '123 456 789 01234',
      },
    })

    const siretField = await screen.findByRole('textbox', {
      name: /SIRET de la structure/,
    })

    await userEvent.clear(siretField)
    await userEvent.tab()

    expect(
      screen.queryByText('Veuillez renseigner un SIRET')
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText(/Vous ne trouvez pas votre adresse/))

    expect(
      screen.getByText(/Revenir à la sélection automatique/)
    ).toBeInTheDocument()

    expect(siretField).not.toHaveValue('Veuillez renseigner un SIRET')
  })

  it('should display tips banner when venue is not virtual', async () => {
    await renderForm()

    const tipsBanner = screen.getByText(
      /Cette adresse s’appliquera par défaut à toutes vos offres, vous pourrez la modifier à l’échelle de chaque offre./
    )

    expect(tipsBanner).toBeInTheDocument()
  })

  it('should update address fields when an address is selected from autocomplete', async () => {
    const apiPatchVenue = vi
      .spyOn(api, 'editVenue')
      .mockResolvedValueOnce(defaultVenue)
    await renderForm({
      venue: {
        ...defaultVenue,
        siret: '123 456 789 01234',
      },
    })

    const addressInput = screen.getByLabelText('Adresse postale *')

    await userEvent.clear(addressInput)
    await userEvent.type(addressInput, '10 rue ')

    const addressSuggestion = await screen.findByText(
      '10 Rue des lilas 69002 Lyon',
      {
        selector: 'span',
      }
    )

    await userEvent.click(addressSuggestion)

    expect(addressInput).toHaveValue('10 Rue des lilas 69002 Lyon')

    await userEvent.click(screen.getByText('Enregistrer'))

    expect(apiPatchVenue).toHaveBeenCalledWith(1, {
      street: '10 Rue des lilas',
      postalCode: '69002',
      city: 'Lyon',
      banId: '1',
      inseeCode: '69002',
      latitude: 11.1,
      longitude: -11.1,
      isManualEdition: false,
      comment: '',
      bookingEmail: 'contact@lieuexemple.com',
      name: 'Lieu de test',
      publicName: 'Lieu Exemple Public',
      siret: '12345678901234',
      withdrawalDetails:
        "Les retraits sont autorisés jusqu'à 24 heures avant l'événement.",
    })
  })

  it('should update address fields when an address is selected from manual', async () => {
    const apiPatchVenue = vi
      .spyOn(api, 'editVenue')
      .mockResolvedValueOnce(defaultVenue)

    await renderForm({
      venue: {
        ...defaultVenue,
        siret: '123 456 789 01234',
      },
    })
    await userEvent.click(screen.getByText(/Vous ne trouvez pas votre adresse/))

    expect(
      screen.getByText(/Revenir à la sélection automatique/)
    ).toBeInTheDocument()

    const disabledAddressInput = screen.getAllByLabelText(/Adresse postale/)[0]
    expect(disabledAddressInput).toBeDisabled()

    const addressInput = screen.getAllByLabelText(/Adresse postale/)[1]

    const cityInput = screen.getByLabelText(/Ville/)
    const postalCodeInput = screen.getByLabelText(/Code postal/)
    const coordsInput = screen.getByLabelText(/Coordonnées GPS/)

    await userEvent.type(addressInput, '10 rue des oiseaux')
    await userEvent.type(cityInput, 'Paris')
    await userEvent.type(postalCodeInput, '75001')
    await userEvent.type(coordsInput, '48.87004, 2.3785')

    await userEvent.click(screen.getByText('Enregistrer'))

    expect(apiPatchVenue).toHaveBeenCalledWith(1, {
      street: '10 rue des oiseaux',
      postalCode: '75001',
      inseeCode: null,
      city: 'Paris',
      latitude: 48.87004,
      longitude: 2.3785,
      banId: null,
      isManualEdition: true,
      bookingEmail: 'contact@lieuexemple.com',
      name: 'Lieu de test',
      publicName: 'Lieu Exemple Public',
      siret: '12345678901234',
      comment: '',
      withdrawalDetails:
        "Les retraits sont autorisés jusqu'à 24 heures avant l'événement.",
    })
  })
})
