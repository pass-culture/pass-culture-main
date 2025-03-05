import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router-dom'
import { expect } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import { apiAdresse } from 'apiClient/adresse/apiAdresse'
import { api } from 'apiClient/api'
import { ApiError, GetVenueResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'
import { Notification } from 'components/Notification/Notification'

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
              <VenueEditionFormScreen venue={venue} />
            </>
          }
        />
      </Routes>
      <Notification />
    </>,
    {
      initialRouterEntries: ['/edition'],
      user: sharedCurrentUserFactory(),
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

vi.mock('apiClient/adresse/apiAdresse', async () => {
  return {
    ...(await vi.importActual('apiClient/adresse/apiAdresse')),
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

vi.mock('commons/utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(),
}))

Element.prototype.scrollIntoView = vi.fn()

vi.mock('commons/core/Venue/siretApiValidate', () => ({
  default: () => Promise.resolve(),
}))

const baseVenue: GetVenueResponseModel = {
  ...defaultGetVenue,
  isPermanent: true,
}

describe('VenueFormScreen', () => {
  it('should display the partner info', async () => {
    renderForm(baseVenue)

    expect(
      await screen.findByText('À propos de votre activité')
    ).toBeInTheDocument()
    expect(
      screen.getByText('État de votre page partenaire sur l’application :')
    ).toBeInTheDocument()
    expect(screen.getByText('Non visible')).toBeInTheDocument()
  })

  it('should mention "structure" instead of "lieu"', () => {
    renderForm({ ...baseVenue, isVirtual: true }, {
      features: ['WIP_ENABLE_OFFER_ADDRESS'],
    })

    expect(
      screen.getByText(
        /Cette structure vous permet uniquement de créer des offres numériques, elle/
      )
    ).toBeInTheDocument()
  })

  describe('when open to public feature is enabled', () => {
    it('should no longer display the partner info', async () => {
      renderForm(baseVenue, {
        features: ['WIP_IS_OPEN_TO_PUBLIC'],
      })

      expect(
        await screen.findByText('À propos de votre activité')
      ).toBeInTheDocument()
      expect(
        screen.queryByText('État de votre page partenaire sur l’application :')
      ).not.toBeInTheDocument()
    })
  })

  describe('on readonly', () => {
    it('should display readonly info', async () => {
      renderForm(
        {
          ...baseVenue,
          description: 'TOTOTO',
          contact: {
            phoneNumber: '123',
            email: 'e@mail.fr',
            website: 'site.web',
          },
        },
        { initialRouterEntries: ['/'] }
      )

      expect(
        await screen.findByText('Vos informations pour le grand public')
      ).toBeInTheDocument()
      expect(screen.getByText('À propos de votre activité')).toBeInTheDocument()
      expect(screen.getByText(/Description/)).toBeInTheDocument()
      expect(screen.getByText(/TOTOTO/)).toBeInTheDocument()
      expect(screen.getByText('Modalités d’accessibilité')).toBeInTheDocument()
      expect(screen.getByText('Informations de contact')).toBeInTheDocument()
      expect(screen.getByText(/Adresse e-mail/)).toBeInTheDocument()
      expect(screen.getByText('e@mail.fr')).toBeInTheDocument()
      expect(screen.getByText(/Téléphone/)).toBeInTheDocument()
      expect(screen.getByText('123')).toBeInTheDocument()
      expect(screen.getByText(/URL de votre site web/)).toBeInTheDocument()
      expect(screen.getByText('site.web')).toBeInTheDocument()
    })

    it('should display the acceslibre section when accessibility is externally defined (via acceslibre)', () => {
      renderForm(
        {
          ...baseVenue,
          externalAccessibilityData: {
            isAccessibleAudioDisability: true,
            isAccessibleMentalDisability: false,
            isAccessibleMotorDisability: true,
            isAccessibleVisualDisability: true,
          },
        },
        {
          initialRouterEntries: ['/'],
        }
      )

      expect(
        screen.queryByText(
          /Votre établissement est accessible aux publics en situation de handicap/
        )
      ).not.toBeInTheDocument()
      expect(
        screen.getByText('Modalités d’accessibilité via acceslibre')
      ).toBeInTheDocument()
    })

    describe('when open to public feature is enabled', () => {
      it('should display a "Accès et horaires" section',() => {
        renderForm(baseVenue, {
          initialRouterEntries: ['/'],
          features: ['WIP_IS_OPEN_TO_PUBLIC'],
        })

        expect(screen.getByText('Accès et horaires')).toBeInTheDocument()
      })

      describe('when the venue is not open to public', () => {
        it('should not display any accessibility section', () => {
          renderForm({ ...baseVenue, isOpenToPublic: false }, {
            initialRouterEntries: ['/'],
            features: ['WIP_IS_OPEN_TO_PUBLIC'],
          })

          expect(screen.queryByText(/Modalités d’accessibilité/)).not.toBeInTheDocument()
        })
      })

      describe('when the venue is open to public', () => {
        it('should display the accessibility section', () => {
          renderForm({ ...baseVenue, isOpenToPublic: true }, {
            initialRouterEntries: ['/'],
            features: ['WIP_IS_OPEN_TO_PUBLIC'],
          })

          expect(screen.queryByText(/Modalités d’accessibilité/)).toBeInTheDocument()
        })
      })
    })
  })

  describe('on edition', () => {
    it('should display an error when the venue could not be updated', async () => {
      renderForm(baseVenue)

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
      // This is necessary to trigger formik dirty state, and allow submitting the form
      await userEvent.type(screen.getByLabelText('Description'), '…')

      await userEvent.click(screen.getByText(/Enregistrer/))

      await waitFor(() => {
        expect(screen.getByText('ensure this is an email')).toBeInTheDocument()
      })
    })

    it('should display the route leaving guard when leaving without saving', async () => {
      renderForm(baseVenue)

      await userEvent.type(screen.getByLabelText('Description'), 'test')
      await userEvent.click(screen.getByText('Annuler'))

      await waitFor(() => {
        expect(
          screen.getByText('Les informations non enregistrées seront perdues')
        ).toBeInTheDocument()
      })
    })

    it('should not send opening hours if the field was not filled, and if there were no opening hours already added previously', async () => {
      const editVenueSpy = vi.spyOn(api, 'editVenue')

      renderForm({ ...baseVenue, openingHours: null })

      // This is necessary to trigger formik dirty state, and allow submitting the form
      await userEvent.type(screen.getByLabelText('Description'), '…')

      await userEvent.click(screen.getByText(/Enregistrer/))

      expect(editVenueSpy).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({ openingHours: null })
      )
    })

    it('should send opening hours if the field was not filled, but the openingHours already existed', async () => {
      const editVenueSpy = vi.spyOn(api, 'editVenue')

      renderForm({
        ...baseVenue,
        openingHours: {
          MONDAY: [
            { open: '09:00', close: '12:00' },
            { open: '13:00', close: '18:00' },
          ],
        },
      })

      // This is necessary to trigger formik dirty state, and allow submitting the form
      await userEvent.type(screen.getByLabelText('Description'), '…')

      await userEvent.click(screen.getByText(/Enregistrer/))

      expect(editVenueSpy).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          openingHours: expect.arrayContaining([
            {
              weekday: 'monday',
              timespan: [
                ['09:00', '12:00'],
                ['13:00', '18:00'],
              ],
            },
          ]),
        })
      )
    })

    describe('when the venue is virtual', () => {
      it('should display a specific message', () => {
        renderForm({ ...baseVenue, isVirtual: true })

        expect(
          screen.getByText(
            /Cette structure vous permet uniquement de créer des offres numériques/
          )
        ).toBeInTheDocument()

        expect(screen.queryAllByRole('input')).toHaveLength(0)
      })

      it('should diplay only some fields', async () => {
        renderForm({ ...baseVenue, isVirtual: true })

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
  })
})
