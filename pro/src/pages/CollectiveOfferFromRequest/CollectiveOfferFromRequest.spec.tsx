import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import * as useAnalytics from '@/app/App/analytics/firebase'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import {
  defaultGetCollectiveOfferRequest,
  getCollectiveOfferManagingOffererFactory,
  getCollectiveOfferTemplateFactory,
  getCollectiveOfferVenueFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { CollectiveOfferFromRequest } from './CollectiveOfferFromRequest'

const offererId = 666
const mockLogEvent = vi.fn()
const mockNavigate = vi.fn()

vi.mock('@/apiClient/api', () => ({
  api: {
    getCollectiveOfferTemplate: vi.fn(),
    getCollectiveOfferRequest: vi.fn(),
    listEducationalDomains: vi.fn(),
    listEducationalOfferers: vi.fn(),
    getNationalPrograms: vi.fn(),
    createCollectiveOffer: vi.fn(),
    attachOfferImage: vi.fn(),
    getVenues: vi.fn(),
  },
}))

vi.mock('react-router', async () => {
  return {
    ...(await vi.importActual('react-router')),
    useParams: () => ({
      offerId: '1',
      requestId: '2',
    }),
    useNavigate: () => mockNavigate,
    default: vi.fn(),
  }
})

describe('CollectiveOfferFromRequest', () => {
  const snackBarError = vi.fn()
  const institution = {
    city: 'Paris',
    institutionId: '123456',
    institutionType: 'LYCEE POLYVALENT',
    name: 'test request clg',
    postalCode: '75000',
  }

  beforeEach(async () => {
    fetchMock.mockResponse((req) => {
      if (req.url === 'https://example.com/image.jpg' && req.method === 'GET') {
        return {
          status: 200,
          body: 'Mock Image Data',
          headers: { 'Content-Type': 'image/jpeg' },
        }
      }
      return { status: 404 }
    })

    const snackBarsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      error: snackBarError,
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
    vi.spyOn(api, 'listEducationalOfferers').mockResolvedValue({
      educationalOfferers: [],
    })
    vi.spyOn(api, 'listEducationalDomains').mockResolvedValue([])
    vi.spyOn(api, 'createCollectiveOffer').mockResolvedValue({ id: 1 })
    vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
  })

  it('should display request information', async () => {
    const collectiveRequest = {
      ...defaultGetCollectiveOfferRequest,
      comment: 'Test unit',
      redactor: {
        email: 'request@example.com',
        firstName: 'Reda',
        lastName: 'Khteur',
      },
      institution,
      dateCreated: '2030-06-20',
      requestedDate: '2030-06-27',
    }

    vi.spyOn(api, 'getCollectiveOfferRequest').mockResolvedValueOnce(
      collectiveRequest
    )

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
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    const collectiveRequest = {
      ...defaultGetCollectiveOfferRequest,
      comment: 'Test unit',
      redactor: {
        ...defaultGetCollectiveOfferRequest.redactor,
        email: 'request@example.com',
      },
      institution,
    }
    vi.spyOn(api, 'getCollectiveOfferRequest').mockResolvedValueOnce(
      collectiveRequest
    )

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
