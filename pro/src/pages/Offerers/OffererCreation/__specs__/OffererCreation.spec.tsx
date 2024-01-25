import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { ApiError, PostOffererResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import { OffererCreation } from '../OffererCreation'

const renderOffererCreation = (options?: RenderWithProvidersOptions) =>
  renderWithProviders(
    <>
      <Routes>
        <Route path="/" element={<OffererCreation />} />
        <Route path="/accueil" element={<div>I’m on homepage</div>} />
      </Routes>
      <Notification />
    </>,
    { initialRouterEntries: ['/'], ...options }
  )

vi.mock('apiClient/api', () => ({
  api: {
    getSirenInfo: vi.fn(),
    createOfferer: vi.fn(),
  },
}))

describe('src | components | OffererCreation', () => {
  it('should render a OffererCreationUnavailable component when pro offerer creation is disabled', () => {
    renderOffererCreation({ features: ['DISABLE_ENTERPRISE_API'] })

    expect(
      screen.getByText('Impossibilité de créer une structure actuellement.')
    ).toBeInTheDocument()
  })

  it('should render a OffererCreation component', async () => {
    renderOffererCreation({})

    await waitFor(() => {
      expect(screen.getByText('Structure')).toBeInTheDocument()
      expect(screen.getByText('Créer')).toBeInTheDocument()
    })
  })

  it('should not be clickable when form is invalid', async () => {
    renderOffererCreation({})

    await userEvent.type(screen.getByLabelText('SIREN *'), '123456')
    await userEvent.tab()

    await userEvent.click(screen.getByText('Créer'))
    expect(
      screen.getByText('Le SIREN doit comporter 9 caractères.')
    ).toBeInTheDocument()
  })

  it('should be clickable when values have been changed and are valid and submit form', async () => {
    vi.spyOn(api, 'getSirenInfo').mockResolvedValue({
      name: 'Ma Petite structure',
      siren: '881457238',
      address: {
        street: '4 rue du test',
        city: 'Plessix-Balisson',
        postalCode: '22350',
      },
      ape_code: '',
    })
    const offerer = {
      id: 1,
    } as PostOffererResponseModel
    vi.spyOn(api, 'createOfferer').mockResolvedValue(offerer)

    renderOffererCreation({})

    await userEvent.type(screen.getByLabelText('SIREN *'), '881457238')
    await userEvent.tab()

    expect(api.getSirenInfo).toHaveBeenCalledTimes(1)

    await userEvent.click(screen.getByText('Créer'))
    expect(api.createOfferer).toHaveBeenCalledWith({
      address: '4 rue du test',
      city: 'Plessix-Balisson',
      name: 'Ma Petite structure',
      postalCode: '22350',
      siren: '881457238',
      apeCode: '',
    })

    expect(screen.getByText('I’m on homepage')).toBeInTheDocument()
  })

  it('should display error on submit fail response', async () => {
    vi.spyOn(api, 'getSirenInfo').mockResolvedValue({
      name: 'Ma Petite structure',
      siren: '881457238',
      address: {
        street: '4 rue du test',
        city: 'Plessix-Balisson',
        postalCode: '22350',
      },
      ape_code: '',
    })

    vi.spyOn(api, 'createOfferer').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 500,
          body: [{ error: ['ERROR'] }],
        } as ApiResult,
        ''
      )
    )

    renderOffererCreation({})

    await userEvent.type(screen.getByLabelText('SIREN *'), '881457238')
    await userEvent.tab()

    await userEvent.click(screen.getByText('Créer'))

    expect(
      screen.getByText('Vous êtes déjà rattaché à cette structure.')
    ).toBeInTheDocument()
  })

  it('should display error on submit if siren has no address', async () => {
    vi.spyOn(api, 'getSirenInfo').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 500,
          body: [{ error: ['ERROR'] }],
        } as ApiResult,
        ''
      )
    )

    renderOffererCreation({})

    await userEvent.type(screen.getByLabelText('SIREN *'), '881457239')
    await userEvent.tab()

    await userEvent.click(screen.getByText('Créer'))

    expect(
      screen.getByText('Impossible de vérifier le SIREN saisi.')
    ).toBeInTheDocument()
  })

  it('should display error on submit if siren is inactive', async () => {
    vi.spyOn(api, 'getSirenInfo').mockResolvedValue({
      name: 'Ma Petite structure',
      siren: '881457238',
      address: {
        street: '4 rue du test',
        city: 'Plessix-Balisson',
        postalCode: '22350',
      },
      ape_code: '',
    })

    vi.spyOn(api, 'createOfferer').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          status: 400,
          body: { siren: ['ERROR'] },
        } as ApiResult,
        ''
      )
    )

    renderOffererCreation({})

    await userEvent.type(screen.getByLabelText('SIREN *'), '881457238')
    await userEvent.tab()

    await userEvent.click(screen.getByText('Créer'))

    expect(
      screen.getByText('Le code SIREN saisi n’est pas valide.')
    ).toBeInTheDocument()
  })

  it('should disable creation button while submitting', async () => {
    vi.spyOn(api, 'getSirenInfo').mockResolvedValue({
      name: 'Ma Petite structure',
      siren: '881457238',
      address: {
        street: '4 rue du test',
        city: 'Plessix-Balisson',
        postalCode: '22350',
      },
      ape_code: '',
    })

    vi.spyOn(api, 'createOfferer').mockRejectedValueOnce({
      id: 1,
    } as PostOffererResponseModel)

    renderOffererCreation({})

    await userEvent.type(screen.getByLabelText('SIREN *'), '881457238')
    await userEvent.tab()

    const creationButton = screen.getByRole('button', { name: 'Créer' })
    expect(creationButton).toBeEnabled()

    // Here we dont wait userEvent.click because we want to test the state of the button before the call end
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    userEvent.click(screen.getByRole('button', { name: 'Créer' }))
    await waitFor(() => {
      expect(creationButton).toBeDisabled()
    })
    await waitFor(() => {
      expect(creationButton).toBeEnabled()
    })
  })
})
