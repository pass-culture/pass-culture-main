import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import createFetchMock from 'vitest-fetch-mock'

import { apiAdresse } from 'apiClient/adresse'
import { api } from 'apiClient/api'
import { ApiError, GetVenueResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import { defaultGetVenue } from 'utils/collectiveApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'utils/renderWithProviders'

import { VenueEditionFormScreen } from '../VenueEditionFormScreen'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

const renderForm = (
  venue: GetVenueResponseModel,
  options?: RenderWithProvidersOptions
) => {
  renderWithProviders(
    <>
      <Routes>
        <Route
          path="*"
          element={
            <>
              <VenueEditionFormScreen venue={venue} reloadVenueData={vi.fn()} />
            </>
          }
        />
      </Routes>
      <Notification />
    </>,
    {
      initialRouterEntries: ['/edition'],
      ...options,
    }
  )
}

vi.mock('apiClient/api', () => ({
  api: {
    postCreateVenue: vi.fn(),
    getSiretInfo: vi.fn(),
    editVenue: vi.fn(),
    getEducationalPartners: vi.fn(() => Promise.resolve({ partners: [] })),
    getAvailableReimbursementPoints: vi.fn(() => Promise.resolve([])),
    canOffererCreateEducationalOffer: vi.fn(),
  },
}))
vi.spyOn(api, 'getSiretInfo').mockResolvedValue({
  active: true,
  address: {
    city: 'paris',
    postalCode: '75008',
    street: 'rue de paris',
  },
  name: 'lieu',
  siret: '88145723823022',
  ape_code: '95.07A',
  legal_category_code: '1000',
})

vi.mock('apiClient/adresse', async () => {
  return {
    ...((await vi.importActual('apiClient/adresse')) ?? {}),
    default: {
      getDataFromAddress: vi.fn(),
    },
  }
})

vi.spyOn(apiAdresse, 'getDataFromAddress').mockResolvedValue([
  {
    address: '12 rue des lilas',
    city: 'Lyon',
    id: '1',
    latitude: 11.1,
    longitude: -11.1,
    label: '12 rue des lilas 69002 Lyon',
    postalCode: '69002',
  },
  {
    address: '12 rue des tournesols',
    city: 'Paris',
    id: '2',
    latitude: 22.2,
    longitude: -2.22,
    label: '12 rue des tournesols 75003 Paris',
    postalCode: '75003',
  },
])

// Mock l’appel à https://api-adresse.data.gouv.fr/search/?limit=${limit}&q=${address}
// Appel fait dans apiAdresse.getDataFromAddress
fetchMock.mockResponse(
  JSON.stringify({
    features: [
      {
        properties: {
          name: 'name',
          city: 'city',
          id: 'id',
          label: 'label',
          postcode: 'postcode',
        },
        geometry: {
          coordinates: [0, 0],
        },
      },
    ],
  }),
  { status: 200 }
)

vi.mock('utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(),
}))

Element.prototype.scrollIntoView = vi.fn()

vi.mock('core/Venue/siretApiValidate', () => ({
  default: () => Promise.resolve(),
}))

describe('VenueFormScreen', () => {
  let venue: GetVenueResponseModel

  beforeEach(() => {
    venue = {
      ...defaultGetVenue,
      isPermanent: true,
    }
  })

  it('should display readonly info', async () => {
    renderForm(venue, { initialRouterEntries: ['/'] })

    expect(
      await screen.findByText('Vos informations pour le grand public')
    ).toBeInTheDocument()
    expect(screen.getByText('À propos de votre activité')).toBeInTheDocument()
    expect(screen.getByText('Modalités d’accessibilité')).toBeInTheDocument()
    expect(screen.getByText('Informations de contact')).toBeInTheDocument()
  })

  it('should display the partner info', async () => {
    renderForm(venue)

    expect(
      await screen.findByText('À propos de votre activité')
    ).toBeInTheDocument()
    expect(
      screen.getByText('État de votre page partenaire sur l’application :')
    ).toBeInTheDocument()
    expect(screen.getByText('Non visible')).toBeInTheDocument()
  })

  it('should display an error when the venue could not be updated', async () => {
    renderForm(venue)

    vi.spyOn(api, 'editVenue').mockRejectedValue(
      new ApiError(
        {} as ApiRequestOptions,
        {
          body: {
            email: ['ensure this is an email'],
          },
        } as ApiResult,
        ''
      )
    )

    await userEvent.click(screen.getByText(/Enregistrer/))

    await waitFor(() => {
      expect(screen.getByText('ensure this is an email')).toBeInTheDocument()
    })
  })

  it('should display specific message when venue is virtual', () => {
    venue.isVirtual = true
    renderForm(venue)

    expect(
      screen.getByText(
        /Ce lieu vous permet uniquement de créer des offres numériques/
      )
    ).toBeInTheDocument()

    expect(screen.queryAllByRole('input')).toHaveLength(0)
  })

  it('should diplay only some fields when the venue is virtual', async () => {
    venue.isVirtual = true

    renderForm(venue)

    await waitFor(() => {
      expect(screen.queryByTestId('wrapper-publicName')).not.toBeInTheDocument()
    })

    expect(screen.queryByTestId('wrapper-description')).not.toBeInTheDocument()
    expect(screen.queryByTestId('wrapper-venueLabel')).not.toBeInTheDocument()
    expect(screen.queryByText('Accessibilité du lieu')).not.toBeInTheDocument()
    expect(
      screen.queryByText('Informations de retrait de vos offres')
    ).not.toBeInTheDocument()
    expect(screen.queryByText('Contact')).not.toBeInTheDocument()
    expect(
      screen.queryByText(
        'Cette adresse s’appliquera par défaut à toutes vos offres, vous pourrez la modifier à l’échelle de chaque offre.'
      )
    ).not.toBeInTheDocument()
  })
})
