import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import * as useAnalytics from 'app/App/analytics/firebase'
import * as useNotification from 'hooks/useNotification'
import {
  getCollectiveOfferManagingOffererFactory,
  getCollectiveOfferTemplateFactory,
  getCollectiveOfferVenueFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { CollectiveOfferFromRequest } from '../CollectiveOfferFromRequest'

const offererId = 666
const mockLogEvent = vi.fn()
const mockNavigate = vi.fn()

vi.mock('apiClient/api', () => ({
  api: {
    getCollectiveOfferTemplate: vi.fn(),
    getCollectiveOfferRequest: vi.fn(),
    getCategories: vi.fn(),
    listEducationalDomains: vi.fn(),
    listEducationalOfferers: vi.fn(),
    getNationalPrograms: vi.fn(),
    createCollectiveOffer: vi.fn(),
    attachOfferImage: vi.fn(),
  },
}))

vi.mock('react-router-dom', async () => {
  return {
    ...(await vi.importActual('react-router-dom')),
    useParams: () => ({
      offerId: '1',
      requestId: '2',
    }),
    useNavigate: () => mockNavigate,
    default: vi.fn(),
  }
})

describe('CollectiveOfferFromRequest', () => {
  const mockNotifyError = vi.fn()
  const institution = {
    city: 'Paris',
    institutionId: '123456',
    institutionType: 'LYCEE POLYVALENT',
    name: 'test request clg',
    postalCode: '75000',
  }

  beforeEach(async () => {
    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: mockNotifyError,
    }))

    vi.spyOn(api, 'getCollectiveOfferTemplate').mockResolvedValue(
      getCollectiveOfferTemplateFactory({
        name: 'mon offre',
        venue: getCollectiveOfferVenueFactory({
          managingOfferer: getCollectiveOfferManagingOffererFactory({
            id: offererId,
          }),
        }),
        dates: {
          end: new Date().toISOString(),
          start: new Date().toISOString(),
        },
      })
    )
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [],
    })
    vi.spyOn(api, 'listEducationalOfferers').mockResolvedValue({
      educationalOfferers: [],
    })
    vi.spyOn(api, 'listEducationalDomains').mockResolvedValue([])
    vi.spyOn(api, 'getNationalPrograms').mockResolvedValue([])
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

  it('should create offer on button click', async () => {
    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
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
      `/offre/collectif/1/creation?structure=${offererId}&requete=2`
    )
  })
})
