import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'
import { expect } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import { api } from '@/apiClient/api'
import { ApiError } from '@/apiClient/v1'
import type { ApiRequestOptions } from '@/apiClient/v1/core/ApiRequestOptions'
import type { ApiResult } from '@/apiClient/v1/core/ApiResult'
import * as useAnalytics from '@/app/App/analytics/firebase'
import {
  SignupJourneyContext,
  type SignupJourneyContextValues,
} from '@/commons/context/SignupJourneyContext/SignupJourneyContext'
import * as getSiretData from '@/commons/core/Venue/getSiretData'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { structureDataBodyModelFactory } from '@/commons/utils/factories/userOfferersFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { Notification } from '@/components/Notification/Notification'

import { DEFAULT_OFFERER_FORM_VALUES } from '../constants'
import { Offerer } from '../Offerer'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

// Mock l’appel à https://data.geopf.fr/geocodage/search/?limit=${limit}&q=${address}
// Appel fait dans getDataFromAddress
vi.mock('@/apiClient/adresse/apiAdresse', () => ({
  getDataFromAddressParts: () =>
    Promise.resolve([
      {
        address: 'name',
        city: 'city',
        id: 'id',
        latitude: 0,
        longitude: 0,
        label: 'label',
        postalCode: 'postcode',
      },
    ]),
}))

// Disable memoization because getSiretData value needs to change
vi.mock('@/commons/utils/memoize', () => ({
  memoize: <T extends (...args: any[]) => any>(func: T): T => {
    return ((...args: Parameters<T>): ReturnType<T> => {
      return func(...args)
    }) as T
  },
}))

const renderOffererScreen = (contextValue: SignupJourneyContextValues) => {
  return renderWithProviders(
    <>
      <SignupJourneyContext.Provider value={contextValue}>
        <Routes>
          <Route
            path="/inscription/structure/recherche"
            element={<Offerer />}
          />
          <Route
            path="/inscription/structure/identification"
            element={<div>Authentication screen</div>}
          />
          <Route
            path="/inscription/structure/rattachement"
            element={<div>Offerers screen</div>}
          />
        </Routes>
      </SignupJourneyContext.Provider>
      <Notification />
    </>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/inscription/structure/recherche'],
    }
  )
}

const mockSetOfferer = vi.fn()
const mockSetInitialAddress = vi.fn()

describe('Offerer', () => {
  let contextValue: SignupJourneyContextValues

  beforeEach(() => {
    contextValue = {
      activity: null,
      offerer: DEFAULT_OFFERER_FORM_VALUES,
      setActivity: () => {},
      setOfferer: mockSetOfferer,
      initialAddress: null,
      setInitialAddress: mockSetInitialAddress,
    }

    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      venues: [],
    })

    vi.spyOn(api, 'getStructureData').mockResolvedValue(
      structureDataBodyModelFactory()
    )
  })

  it('should render component', async () => {
    contextValue.offerer = null
    renderOffererScreen(contextValue)

    expect(
      await screen.findByText(
        'Renseignez le SIRET de la structure à laquelle vous êtes rattaché.'
      )
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('button', { name: 'Continuer' })
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Étape précédente' })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByText('Modifier la visibilité de mon SIRET')
    ).not.toBeInTheDocument()

    expect(
      screen.getByText(
        'Vous êtes un équipement d’une collectivité ou d’un établissement public ?'
      )
    ).toBeInTheDocument()

    expect(
      screen.getByRole('link', { name: /En savoir plus/ })
    ).toHaveAttribute(
      'href',
      'https://aide.passculture.app/hc/fr/articles/4633420022300--Acteurs-Culturels-Collectivit%C3%A9-Lieu-rattach%C3%A9-%C3%A0-une-collectivit%C3%A9-S-inscrire-et-param%C3%A9trer-son-compte-pass-Culture-'
    )

    expect(
      screen.getByRole('link', {
        name: /Vous ne connaissez pas votre SIRET \? Consultez l'Annuaire des Entreprises/,
      })
    ).toHaveAttribute('href', 'https://annuaire-entreprises.data.gouv.fr/')
  })

  it('should not display authentication screen on submit with form error', async () => {
    vi.spyOn(api, 'getStructureData').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            global: ["Le SIRET n'existe pas"],
          },
        } as ApiResult,
        ''
      )
    )

    renderOffererScreen(contextValue)

    expect(
      screen.getByText('Dites-nous pour quelle structure vous travaillez')
    ).toBeInTheDocument()

    expect(await screen.findByText('Obligatoire')).toBeInTheDocument()

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678999999'
    )

    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(await screen.findByText("Le SIRET n'existe pas")).toBeInTheDocument()
    expect(api.getStructureData).toHaveBeenCalled()
    expect(screen.queryByText('Authentication screen')).not.toBeInTheDocument()
    expect(
      screen.getByText('Dites-nous pour quelle structure vous travaillez')
    ).toBeInTheDocument()
  })

  it('should not render offerers screen on submit if venuesList is empty', async () => {
    renderOffererScreen(contextValue)

    expect(
      await screen.findByText(
        'Dites-nous pour quelle structure vous travaillez'
      )
    ).toBeInTheDocument()
    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(screen.queryByText('Offerers screen')).not.toBeInTheDocument()
  })

  it('should submit the form when clicking the continue button', async () => {
    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      offererSiren: '123456789',
      venues: [
        { id: 1, name: 'First Venue', isPermanent: true },
        { id: 2, name: 'Second Venue', isPermanent: true },
      ],
    })
    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    expect(mockSetInitialAddress).toHaveBeenCalledWith({
      banId: '49759_1304_00002',
      city: 'Paris',
      inseeCode: '75056',
      latitude: 48.869440910282734,
      longitude: 2.3087717501609233,
      postalCode: '75001',
      street: '4 rue Carnot',
      addressAutocomplete: '4 rue Carnot 75001 Paris',
      'search-addressAutocomplete': '4 rue Carnot 75001 Paris',
    })
    expect(mockSetOfferer).toHaveBeenCalledWith({
      apeCode: '9003A',
      hasVenueWithSiret: false,
      name: 'ma super stucture',
      siren: '123456789',
      siret: '12345678933333',
      banId: '49759_1304_00002',
      city: 'Paris',
      inseeCode: '75056',
      latitude: 48.869440910282734,
      longitude: 2.3087717501609233,
      postalCode: '75001',
      street: '4 rue Carnot',
      isDiffusible: true,
    })
    expect(api.getVenuesOfOffererFromSiret).toHaveBeenCalled()
  })

  it('should redirect to offerers page if the offerer has a venue with the same siret', async () => {
    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      offererSiren: '123456789',
      venues: [
        {
          id: 1,
          name: 'First Venue',
          isPermanent: true,
          siret: '12345678933333',
        },
        { id: 2, name: 'Second Venue', isPermanent: true },
      ],
    })
    vi.spyOn(getSiretData, 'getSiretData').mockResolvedValue({
      location: null,
      apeCode: '75',
      isDiffusible: true,
      name: 'name',
      siren: '123456789',
      siret: '12345678933333',
    })

    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    await waitFor(() => {
      expect(screen.getByText('Offerers screen')).toBeInTheDocument()
    })
  })

  it('should redirect to identification page if the offerer has no venue with the same siret', async () => {
    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      offererSiren: '123456789',
      venues: [
        {
          id: 1,
          name: 'First Venue',
          isPermanent: true,
        },
        { id: 2, name: 'Second Venue', isPermanent: true },
      ],
    })
    vi.spyOn(getSiretData, 'getSiretData').mockResolvedValue({
      location: null,
      apeCode: '75',
      isDiffusible: true,
      name: 'name',
      siren: '123456789',
      siret: '12345678933333',
    })

    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    await waitFor(() => {
      expect(screen.getByText('Authentication screen')).toBeInTheDocument()
    })
  })

  it('should display errors on api failure', async () => {
    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 500,
          body: [{ error: ['ERROR'] }],
        } as ApiResult,
        ''
      )
    )
    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    await waitFor(() => {
      expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
    })
  })

  it('should display BannerInvisibleSiren on error 400 with specific message', async () => {
    vi.spyOn(api, 'getStructureData').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            global: [
              "Le propriétaire de ce SIRET s'oppose à la diffusion de ses données au public",
            ],
          },
        } as ApiResult,
        ''
      )
    )
    renderOffererScreen(contextValue)

    expect(
      screen.queryByText('Modifier la visibilité de mon SIRET')
    ).not.toBeInTheDocument()

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933367'
    )

    await waitFor(() => {
      expect(
        screen.getByLabelText(/Numéro de SIRET à 14 chiffres/)
      ).toHaveValue('12345678933367')
    })
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(api.getStructureData).toHaveBeenCalled()
    expect(
      screen.getByText('Modifier la visibilité de mon SIRET')
    ).toBeInTheDocument()
  })

  it('should not display MaybeAppUserDialog component on submit with valid apeCode', async () => {
    renderOffererScreen(contextValue)

    await userEvent.click(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/)
    )
    await userEvent.tab()
    expect(api.getStructureData).not.toHaveBeenCalled()

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933338'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(api.getStructureData).toHaveBeenCalled()
    expect(
      screen.queryByText('Il semblerait que tu ne sois pas')
    ).not.toBeInTheDocument()
  })

  it('should not display MaybeAppUserDialog component if siret is incorrect', async () => {
    vi.spyOn(api, 'getStructureData').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 500,
          body: [{ error: ['ERROR'] }],
        } as ApiResult,
        ''
      )
    )
    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933334'
    )

    await waitFor(() => {
      expect(
        screen.getByLabelText(/Numéro de SIRET à 14 chiffres/)
      ).toHaveValue('12345678933334')
    })
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(api.getStructureData).toHaveBeenCalled()
    expect(
      screen.queryByText('Il semblerait que tu ne sois pas')
    ).not.toBeInTheDocument()
  })

  it('should display MaybeAppUserDialog and hide on cancel button', async () => {
    vi.spyOn(api, 'getStructureData').mockResolvedValue(
      structureDataBodyModelFactory({ apeCode: '8531Z' })
    )
    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933335'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(api.getStructureData).toHaveBeenCalled()

    await waitFor(() => {
      expect(
        screen.getByText('Êtes-vous un professionnel de la culture ?')
      ).toBeInTheDocument()
    })

    expect(
      screen.getByText(
        /Seuls les professionnels sont habilités à rejoindre l’espace pass Culture Pro/
      )
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Continuer vers le pass Culture Pro',
      })
    )

    await waitFor(() => {
      expect(
        screen.queryByText('Il semblerait que tu ne sois pas')
      ).not.toBeInTheDocument()
    })
  })

  it('should display MaybeAppUserDialog for higher edication', async () => {
    vi.spyOn(api, 'getStructureData').mockResolvedValue(
      structureDataBodyModelFactory({ apeCode: '8542Z' })
    )
    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678933335'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(api.getStructureData).toHaveBeenCalled()

    await waitFor(() => {
      expect(
        screen.getByText(
          "Travaillez-vous pour un établissement d'enseignement supérieur ?"
        )
      ).toBeInTheDocument()
    })

    expect(
      screen.getByText(
        /Seuls les professionnels sont habilités à rejoindre l’espace pass Culture Pro/
      )
    ).toBeInTheDocument()
  })

  it("should render error message when siret doesn't exist", async () => {
    vi.spyOn(api, 'getStructureData').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            global: ["Le SIRET n'existe pas"],
          },
        } as ApiResult,
        ''
      )
    )

    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678999999'
    )
    await userEvent.click(screen.getByText('Continuer'))
    expect(await screen.findByText("Le SIRET n'existe pas")).toBeInTheDocument()
  })

  it('should render error message when siret is not visible', async () => {
    vi.spyOn(api, 'getStructureData').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            global: [
              "Le propriétaire de ce SIRET s'oppose à la diffusion de ses données au public",
            ],
          },
        } as ApiResult,
        ''
      )
    )

    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      '12345678900001'
    )
    await userEvent.click(screen.getByText('Continuer'))
    expect(
      await screen.findByText(
        "Le propriétaire de ce SIRET s'oppose à la diffusion de ses données au public"
      )
    ).toBeInTheDocument()
  })

  it('should render offerer form', async () => {
    renderOffererScreen(contextValue)

    expect(
      await screen.findByText(
        'Dites-nous pour quelle structure vous travaillez'
      )
    ).toBeInTheDocument()

    expect(screen.getByLabelText(/Numéro de SIRET à 14 chiffres/)).toHaveValue(
      ''
    )
  })

  it('should fill siret field only with numbers', async () => {
    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      'AbdqsI'
    )

    expect(screen.getByLabelText(/Numéro de SIRET à 14 chiffres/)).toHaveValue(
      ''
    )
  })

  it('should render empty siret field error', async () => {
    renderOffererScreen(contextValue)

    await userEvent.click(screen.getByText('Continuer'))
    expect(
      await screen.findByText('Veuillez renseigner un SIRET')
    ).toBeInTheDocument()
  })

  it('should log event when unknown siret link clicked', async () => {
    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    renderOffererScreen(contextValue)
    await userEvent.click(
      screen.getByText(
        /Vous ne connaissez pas votre SIRET \? Consultez l'Annuaire des Entreprises\./
      )
    )
    expect(mockLogEvent).toHaveBeenNthCalledWith(1, 'hasClickedUnknownSiret', {
      from: '/',
    })
  })

  const lenErrorCondition = ['22223333', '1234567891234567']
  it.each(lenErrorCondition)('should render errors', async (siretValue) => {
    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET à 14 chiffres/),
      siretValue
    )
    await userEvent.click(screen.getByText('Continuer'))
    expect(
      await screen.findByText('Le SIRET doit comporter 14 caractères')
    ).toBeInTheDocument()
  })
})
