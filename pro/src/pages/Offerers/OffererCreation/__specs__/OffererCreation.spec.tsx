import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Route, Routes } from 'react-router-dom'

import { api } from 'apiClient/api'
import { ApiError, GetOffererResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import { renderWithProviders } from 'utils/renderWithProviders'

import OffererCreation from '../OffererCreation'
const renderOffererCreation = async (storeOverrides: any) =>
  renderWithProviders(
    <>
      <Routes>
        <Route path="/" element={<OffererCreation />} />
        <Route path="/accueil" element={<div>I'm on homepage</div>} />
      </Routes>
      <Notification />
    </>,
    { storeOverrides, initialRouterEntries: ['/'] }
  )

jest.mock('apiClient/api', () => ({
  api: {
    getSirenInfo: jest.fn(),
    createOfferer: jest.fn(),
  },
}))

describe('src | components | OffererCreation', () => {
  it('should render a OffererCreationUnavailable component when pro offerer creation is disabled', async () => {
    const store = {
      features: {
        initialized: true,
        list: [
          {
            description: 'Active feature',
            id: 'DISABLE_ENTERPRISE_API',
            isActive: true,
            name: 'DISABLE_ENTERPRISE_API',
            nameKey: 'DISABLE_ENTERPRISE_API',
          },
        ],
      },
    }

    renderOffererCreation(store)

    expect(
      await screen.getByText(
        'Impossibilité de créer une structure actuellement.'
      )
    ).toBeInTheDocument()
  })

  it('should render a OffererCreation component and creation button should not be clickable', async () => {
    renderOffererCreation({})

    await waitFor(() => {
      expect(screen.getByText('Structure')).toBeInTheDocument()
      expect(screen.getByText('Créer')).toBeInTheDocument()
    })
  })

  it('should not be clickable when form is invalid', async () => {
    renderOffererCreation({})

    await userEvent.type(await screen.getByLabelText('SIREN'), '123456')
    await userEvent.tab()

    expect(screen.getByText('Créer')).toBeDisabled()
  })

  it('should be clickable when values have been changed and are valid and submit form', async () => {
    jest.spyOn(api, 'getSirenInfo').mockResolvedValue({
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
    } as GetOffererResponseModel
    jest.spyOn(api, 'createOfferer').mockResolvedValue(offerer)

    renderOffererCreation({})

    await userEvent.type(await screen.getByLabelText('SIREN'), '881457238')
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

    expect(screen.getByText("I'm on homepage")).toBeInTheDocument()
  })

  it('should display error on submit fail response', async () => {
    jest.spyOn(api, 'getSirenInfo').mockResolvedValue({
      name: 'Ma Petite structure',
      siren: '881457238',
      address: {
        street: '4 rue du test',
        city: 'Plessix-Balisson',
        postalCode: '22350',
      },
      ape_code: '',
    })

    jest.spyOn(api, 'createOfferer').mockRejectedValue(
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

    await userEvent.type(await screen.getByLabelText('SIREN'), '881457238')
    await userEvent.tab()

    await userEvent.click(screen.getByText('Créer'))

    expect(
      screen.getByText('Vous étes déjà rattaché à cette structure.')
    ).toBeInTheDocument()
  })

  it('should display error on submit if siren has no address', async () => {
    jest.spyOn(api, 'getSirenInfo').mockRejectedValue(
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

    await userEvent.type(await screen.getByLabelText('SIREN'), '881457239')
    await userEvent.tab()

    await userEvent.click(screen.getByText('Créer'))

    expect(
      screen.getByText('Impossible de vérifier le SIREN saisi.')
    ).toBeInTheDocument()
  })
})
