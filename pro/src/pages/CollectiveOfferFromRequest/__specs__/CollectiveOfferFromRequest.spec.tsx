import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import router from 'react-router-dom'

import { api } from 'apiClient/api'
import * as useAnalytics from 'hooks/useAnalytics'
import * as useNotification from 'hooks/useNotification'
import { defaultCollectifOfferResponseModel } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferFromRequest from '../CollectiveOfferFromRequest'

const mockLogEvent = vi.fn()

vi.mock('apiClient/api', () => ({
  api: {
    getCollectiveOfferTemplate: vi.fn(),
    getCollectiveOfferRequest: vi.fn(),
    getCategories: vi.fn(),
    listEducationalDomains: vi.fn(),
    listEducationalOfferers: vi.fn(),
    createCollectiveOffer: vi.fn(),
  },
}))

vi.mock('react-router-dom', () => ({
  ...vi.importActual('react-router-dom'),
  useParams: () => ({
    offerId: vi.fn(),
    requestId: vi.fn(),
  }),
  useNavigate: vi.fn(),
}))

describe('CollectiveOfferFromRequest', () => {
  const notifyError = vi.fn()
  const mockNavigate = vi.fn()
  const institution = {
    city: 'Paris',
    institutionId: '123456',
    institutionType: 'LYCEE POLYVALENT',
    name: 'test request clg',
    postalCode: '75000',
  }

  beforeEach(() => {
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...vi.importActual('hooks/useNotification'),
      error: notifyError,
    }))

    jest
      .spyOn(api, 'getCollectiveOfferTemplate')
      .mockResolvedValue(defaultCollectifOfferResponseModel)
    jest
      .spyOn(router, 'useParams')
      .mockReturnValue({ offerId: '1', requestId: '2' })
    vi.spyOn(router, 'useNavigate').mockReturnValue(mockNavigate)
    jest
      .spyOn(api, 'getCategories')
      .mockResolvedValue({ categories: [], subcategories: [] })
    jest
      .spyOn(api, 'listEducationalOfferers')
      .mockResolvedValue({ educationalOfferers: [] })
    vi.spyOn(api, 'listEducationalDomains').mockResolvedValue([])
    vi.spyOn(api, 'createCollectiveOffer').mockResolvedValue({ id: 1 })
  })
  it('should display request information', async () => {
    vi.spyOn(api, 'getCollectiveOfferRequest').mockResolvedValueOnce({
      comment: 'Test unit',
      redactor: {
        email: 'request@example.com',
        firstName: 'Reda',
        lastName: 'Khteur',
      },
      institution,
      dateCreated: '2030-06-20',
      requestedDate: '2030-06-27',
    })

    renderWithProviders(<CollectiveOfferFromRequest />)

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    expect(api.getCollectiveOfferTemplate).toHaveBeenCalledTimes(1)
    expect(api.getCollectiveOfferRequest).toHaveBeenCalledTimes(1)

    expect(screen.getByText('request@example.com')).toBeInTheDocument()
    expect(screen.getByText('Test unit')).toBeInTheDocument()
    expect(screen.getByText('mon offre')).toBeInTheDocument()
    expect(screen.getByText('20 juin 2030')).toBeInTheDocument()
    expect(
      screen.getByText(/LYCEE POLYVALENT test request clg/)
    ).toBeInTheDocument()
    expect(screen.getByText(/75000 Paris/)).toBeInTheDocument()
    expect(screen.getByText('27 juin 2030')).toBeInTheDocument()
  })

  it('should display spinner when id params doesnt exist', async () => {
    vi.spyOn(router, 'useParams').mockReturnValue({ offerId: '' })
    renderWithProviders(<CollectiveOfferFromRequest />)

    expect(await screen.findByText('Chargement en cours')).toBeInTheDocument()
  })

  it('should call api and get error', async () => {
    vi.spyOn(api, 'getCollectiveOfferTemplate').mockRejectedValueOnce({
      isOk: false,
      message: 'Une erreur est survenue lors de la récupération de votre offre',
      payload: null,
    })
    vi.spyOn(api, 'getCollectiveOfferRequest').mockRejectedValueOnce({
      isOk: false,
      message: 'Une erreur est survenue lors de la récupération de votre offre',
      payload: null,
    })

    renderWithProviders(<CollectiveOfferFromRequest />)

    expect(await screen.findByText('Chargement en cours')).toBeInTheDocument()

    expect(notifyError).toHaveBeenNthCalledWith(
      1,
      'Une erreur est survenue lors de la récupération de votre offre'
    )
    expect(notifyError).toHaveBeenNthCalledWith(
      2,
      'Nous avons rencontré un problème lors de la récupération des données.'
    )
  })

  it('should create offer on button click', async () => {
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))

    vi.spyOn(api, 'getCollectiveOfferRequest').mockResolvedValueOnce({
      comment: 'Test unit',
      redactor: { email: 'request@example.com' },
      institution,
    })

    renderWithProviders(<CollectiveOfferFromRequest />)

    await waitForElementToBeRemoved(() => screen.queryByTestId('spinner'))

    const requestButton = screen.getByText('Créer l’offre pour l’enseignant')

    await userEvent.click(requestButton)

    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockNavigate).toHaveBeenCalledWith(
      '/offre/collectif/1/creation?structure=1&requete=2'
    )
  })
})
