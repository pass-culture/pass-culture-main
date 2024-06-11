import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'
import createFetchMock from 'vitest-fetch-mock'

import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { DEFAULT_ADDRESS_FORM_VALUES } from 'components/Address/constants'
import { Notification } from 'components/Notification/Notification'
import {
  SignupJourneyContext,
  SignupJourneyContextValues,
} from 'context/SignupJourneyContext/SignupJourneyContext'
import * as siretApiValidate from 'core/Venue/siretApiValidate'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { DEFAULT_OFFERER_FORM_VALUES } from '../constants'
import { Offerer } from '../Offerer'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

vi.spyOn(siretApiValidate, 'siretApiValidate').mockResolvedValue(null)

// Mock l’appel à https://api-adresse.data.gouv.fr/search/?limit=${limit}&q=${address}
// Appel fait dans apiAdresse.getDataFromAddress
vi.mock('apiClient/adresse/apiAdresse', () => ({
  apiAdresse: {
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
  },
}))

const renderOffererScreen = (contextValue: SignupJourneyContextValues) => {
  return renderWithProviders(
    <>
      <SignupJourneyContext.Provider value={contextValue}>
        <Routes>
          <Route path="/parcours-inscription/structure" element={<Offerer />} />
          <Route
            path="/parcours-inscription/identification"
            element={<div>Authentication screen</div>}
          />
          <Route
            path="/parcours-inscription/structure/rattachement"
            element={<div>Offerers screen</div>}
          />
        </Routes>
      </SignupJourneyContext.Provider>
      <Notification />
    </>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: ['/parcours-inscription/structure'],
    }
  )
}

describe('Offerer', () => {
  let contextValue: SignupJourneyContextValues

  beforeEach(() => {
    contextValue = {
      activity: null,
      offerer: DEFAULT_OFFERER_FORM_VALUES,
      setActivity: () => {},
      setOfferer: () => {},
    }

    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      venues: [],
    })

    vi.spyOn(api, 'getSiretInfo').mockResolvedValue({
      active: true,
      address: {
        city: 'Paris',
        postalCode: '75008',
        street: 'rue du test',
      },
      name: 'Test',
      siret: '12345678933333',
      ape_code: '95.01A',
      legal_category_code: '1000',
    })
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
    ).toBeInTheDocument()
  })

  it('should display authentication signup journey if offerer is set', () => {
    contextValue.offerer = {
      siret: '12345678933333',
      name: 'Test',
      hasVenueWithSiret: false,
      ...DEFAULT_ADDRESS_FORM_VALUES,
    }

    renderOffererScreen(contextValue)
    expect(screen.getByText('Authentication screen')).toBeInTheDocument()
  })

  it('should not display authentication screen on submit with form error', async () => {
    vi.spyOn(api, 'getSiretInfo').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 422,
          body: [{ error: ['No SIRET'] }],
        } as ApiResult,
        ''
      )
    )

    renderOffererScreen(contextValue)

    expect(
      screen.getByText('Renseignez le SIRET de votre structure')
    ).toBeInTheDocument()

    await userEvent.type(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *'),
      '12345678999999'
    )

    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(await screen.findByText("Le SIRET n'existe pas")).toBeInTheDocument()
    expect(api.getSiretInfo).toHaveBeenCalled()
    expect(screen.queryByText('Authentication screen')).not.toBeInTheDocument()
    expect(
      screen.getByText('Renseignez le SIRET de votre structure')
    ).toBeInTheDocument()
  })

  it('should not render offerers screen on submit if venuesList is empty', async () => {
    renderOffererScreen(contextValue)

    expect(
      await screen.findByText('Renseignez le SIRET de votre structure')
    ).toBeInTheDocument()
    await userEvent.type(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *'),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(screen.queryByText('Offerers screen')).not.toBeInTheDocument()
  })

  it('should submit the form when clicking the continue button', async () => {
    vi.spyOn(api, 'getVenuesOfOffererFromSiret').mockResolvedValue({
      venues: [
        { id: 1, name: 'First Venue', isPermanent: true },
        { id: 2, name: 'Second Venue', isPermanent: true },
      ],
    })
    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *'),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    expect(api.getVenuesOfOffererFromSiret).toHaveBeenCalled()
  })

  it('should redirect to offerers page if the offerer has a venue with the same siret', async () => {
    contextValue.offerer = {
      name: 'name',
      siret: '12345678933333',
      hasVenueWithSiret: true,
      ...DEFAULT_ADDRESS_FORM_VALUES,
    }
    renderOffererScreen(contextValue)

    await waitFor(() => {
      expect(screen.getByText('Offerers screen')).toBeInTheDocument()
    })
  })

  it('should redirect to identification page if the offerer has no venue with the same siret', async () => {
    contextValue.offerer = {
      name: 'name',
      siret: '12345678933333',
      hasVenueWithSiret: false,
      ...DEFAULT_ADDRESS_FORM_VALUES,
    }
    renderOffererScreen(contextValue)

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
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *'),
      '12345678933333'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    await waitFor(() => {
      expect(screen.getByText('Une erreur est survenue')).toBeInTheDocument()
    })
  })

  it('should display BannerInvisibleSiren on error 400 with specific message', async () => {
    vi.spyOn(api, 'getSiretInfo').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            global: [
              'Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles.',
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
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *'),
      '12345678933367'
    )

    await waitFor(() => {
      expect(
        screen.getByLabelText('Numéro de SIRET à 14 chiffres *')
      ).toHaveValue('123 456 789 33367')
    })
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(api.getSiretInfo).toHaveBeenCalled()
    expect(
      screen.getByText('Modifier la visibilité de mon SIRET')
    ).toBeInTheDocument()
  })

  it('should not display MaybeAppUserDialog component on submit with valid apeCode', async () => {
    renderOffererScreen(contextValue)

    await userEvent.click(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *')
    )
    await userEvent.tab()
    expect(api.getSiretInfo).not.toHaveBeenCalled()

    await userEvent.type(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *'),
      '12345678933338'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(api.getSiretInfo).toHaveBeenCalled()
    expect(
      screen.queryByText('Il semblerait que tu ne sois pas')
    ).not.toBeInTheDocument()
  })

  it('should not display MaybeAppUserDialog component if siret is incorrect', async () => {
    vi.spyOn(api, 'getSiretInfo').mockRejectedValue(
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
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *'),
      '12345678933334'
    )

    await waitFor(() => {
      expect(
        screen.getByLabelText('Numéro de SIRET à 14 chiffres *')
      ).toHaveValue('123 456 789 33334')
    })
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(api.getSiretInfo).toHaveBeenCalled()
    expect(
      screen.queryByText('Il semblerait que tu ne sois pas')
    ).not.toBeInTheDocument()
  })

  it('should display MaybeAppUserDialog and hide on cancel button', async () => {
    vi.spyOn(api, 'getSiretInfo').mockResolvedValue({
      active: true,
      address: {
        city: 'Paris',
        postalCode: '75008',
        street: 'rue du test',
      },
      name: 'Test',
      siret: '12345678933335',
      ape_code: '85.31Z',
      legal_category_code: '1000',
    })
    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *'),
      '12345678933335'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(api.getSiretInfo).toHaveBeenCalled()

    await waitFor(() => {
      expect(
        screen.getByText('Il semblerait que tu ne sois pas')
      ).toBeInTheDocument()
    })

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

  it("should render error message when siret doesn't exist", async () => {
    vi.spyOn(api, 'getSiretInfo').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 422,
          body: [{ error: ['No SIRET'] }],
        } as ApiResult,
        ''
      )
    )

    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *'),
      '12345678999999'
    )
    await userEvent.click(screen.getByText('Continuer'))
    expect(await screen.findByText("Le SIRET n'existe pas")).toBeInTheDocument()
  })

  it('should render error message when siret is not visible', async () => {
    vi.spyOn(api, 'getSiretInfo').mockRejectedValueOnce(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: {
            global: [
              'Les informations relatives à ce SIREN ou SIRET ne sont pas accessibles.',
            ],
          },
        } as ApiResult,
        ''
      )
    )

    renderOffererScreen(contextValue)

    await userEvent.type(
      screen.getByLabelText('Numéro de SIRET à 14 chiffres *'),
      '12345678900001'
    )
    await userEvent.click(screen.getByText('Continuer'))
    expect(
      await screen.findByText(
        "Le propriétaire de ce SIRET s'oppose à la diffusion de ses données au public"
      )
    ).toBeInTheDocument()
  })
})
