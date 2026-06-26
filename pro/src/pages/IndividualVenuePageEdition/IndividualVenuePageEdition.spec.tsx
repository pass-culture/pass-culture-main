import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'
import type { SWRResponse } from 'swr'
import { expect, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import * as apiAdresse from '@/apiClient/adresse/apiAdresse'
import { api } from '@/apiClient/api'
import type { ApiRequestOptions, ApiResult } from '@/apiClient/compat'
import { ApiError } from '@/apiClient/compat'
import { DisplayableActivity, type GetVenueResponseModel } from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { getVolunteeringUrlError } from '@/commons/core/VenueEdition/getVolunteeringUrlError'
import * as useEducationalDomains from '@/commons/hooks/swr/useEducationalDomains'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { IndividualVenuePageEdition } from './IndividualVenuePageEdition'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

function renderForm(
  venueOverrides: Partial<GetVenueResponseModel> = {},
  options?: RenderWithProvidersOptions
) {
  const Wrapper = () => {
    return <IndividualVenuePageEdition />
  }

  options = {
    initialRouterEntries: ['/edition'],
    user: sharedCurrentUserFactory(),
    ...options,
  }

  renderWithProviders(
    <>
      <Routes>
        <Route path="*" element={<Wrapper />} />
      </Routes>
      <SnackBarContainer />
    </>,
    {
      ...options,
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
          selectedPartnerVenue: makeGetVenueResponseModel({
            id: 1,
            ...venueOverrides,
          }),
        },
      },
    }
  )
}

vi.mock('@/apiClient/api', () => ({
  api: {
    postCreateVenue: vi.fn(),
    getSiretInfo: vi.fn(),
    editVenue: vi.fn(),
    getAvailableReimbursementPoints: vi.fn(() => Promise.resolve([])),
    canOffererCreateEducationalOffer: vi.fn(),
    getVenue: vi.fn(),
  },
}))

vi.mock('@/apiClient/adresse/apiAdresse', async () => {
  return {
    ...(await vi.importActual('@/apiClient/adresse/apiAdresse')),
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
    inseeCode: '69002',
  },
  {
    address: '12 rue des tournesols',
    city: 'Paris',
    id: '2',
    latitude: 22.2,
    longitude: -2.22,
    label: '12 rue des tournesols 75003 Paris',
    postalCode: '75003',
    inseeCode: '75003',
  },
])

vi.mock('@/commons/hooks/useSyncVenueCache', () => ({
  useSyncVenueCache: () => ({
    syncVenue: vi.fn(),
    syncVenueWithData: vi.fn(),
  }),
}))

vi.mock('swr', async (importOriginal) => ({
  ...(await importOriginal()),
  default: vi.fn(),
}))

// Mock l’appel à https://data.geopf.fr/geocodage/search/?limit=${limit}&q=${address}
// Appel fait dans getDataFromAddress
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

vi.mock('@/commons/utils/windowMatchMedia', () => ({
  doesUserPreferReducedMotion: vi.fn(),
}))

Element.prototype.scrollIntoView = vi.fn()

vi.mock('@/commons/core/Venue/siretApiValidate', () => ({
  default: () => Promise.resolve(),
}))

const mockLogEvent = vi.fn()

vi.mock('@/commons/core/VenueEdition/getVolunteeringUrlError', () => ({
  getVolunteeringUrlError: vi.fn(),
}))

const baseVenue: GetVenueResponseModel = {
  ...defaultGetVenue,
  isPermanent: true,
}

describe('IndividualVenuePageEdition', () => {
  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    vi.mocked(getVolunteeringUrlError).mockReturnValue(undefined)
    vi.spyOn(useEducationalDomains, 'useEducationalDomains').mockImplementation(
      () => {
        return {
          isLoading: false,
          data: [
            {
              id: 1,
              name: 'domaine 1',
              nationalPrograms: [],
            },
            {
              id: 2,
              name: 'domaine b',
              nationalPrograms: [],
            },
            {
              id: 3,
              name: 'domaine III',
              nationalPrograms: [],
            },
          ],
        } as SWRResponse
      }
    )
  })
  it('should display access to partner page is impossible warning', async () => {
    const venue: GetVenueResponseModel = {
      ...defaultGetVenue,
      isPermanent: true,
      hasOffers: true,
      hasActiveIndividualOffer: false,
    }

    renderForm(venue)

    await waitFor(() => {
      expect(
        screen.getByText(
          "Publiez une offre pour rendre votre page accessible aux jeunes dans l'application."
        )
      ).toBeInTheDocument()
    })
  })

  // See VenueEdition.spec.tsx for additional tests.
  describe('on edition (VenueEditionForm)', () => {
    describe('about accessibility', () => {
      it('should check none accessibility', async () => {
        renderForm({
          ...baseVenue,
          siret: null,
          visualDisabilityCompliant: false,
          mentalDisabilityCompliant: false,
          audioDisabilityCompliant: false,
          motorDisabilityCompliant: false,
        })

        expect(
          await screen.findByLabelText('Non accessible', { exact: false })
        ).toBeChecked()
      })

      it('should not check none accessibility if every accessibility parameters are null', async () => {
        renderForm({
          ...baseVenue,
          visualDisabilityCompliant: null,
          mentalDisabilityCompliant: null,
          audioDisabilityCompliant: null,
          motorDisabilityCompliant: null,
        })

        expect(
          await screen.findByLabelText('Non accessible', { exact: false })
        ).not.toBeChecked()
      })

      it('should display the acces libre callout for permanent venues', async () => {
        renderForm({ ...baseVenue, isPermanent: true })

        expect(
          await screen.findByText(
            /Complétez les modalités d'accessibilité de votre établissement sur acceslibre.beta.gouv.fr/
          )
        ).toBeInTheDocument()
      })
    })

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

    it('should not display the route leaving guard when clicking Annuler with unsaved changes', async () => {
      renderForm(baseVenue)

      await userEvent.type(screen.getByLabelText('Description'), 'test')
      await userEvent.click(screen.getByText('Annuler'))

      await waitFor(() => {
        expect(
          screen.queryByText('Les informations non enregistrées seront perdues')
        ).not.toBeInTheDocument()
      })
    })

    it('should not display the route leaving guard when clicking Annuler after accessibility change', async () => {
      renderForm(baseVenue)

      await userEvent.click(screen.getByRole('checkbox', { name: 'Moteur' }))
      await userEvent.click(screen.getByText('Annuler'))

      await waitFor(() => {
        expect(
          screen.queryByText('Les informations non enregistrées seront perdues')
        ).not.toBeInTheDocument()
      })
    })

    it('should not display the route leaving guard when leaving without any change', async () => {
      renderForm(baseVenue)

      await userEvent.click(screen.getByText('Annuler'))

      await waitFor(() => {
        expect(
          screen.queryByText('Les informations non enregistrées seront perdues')
        ).not.toBeInTheDocument()
      })
    })

    it('should not send opening hours if the field was not filled, and if there were no opening hours already added previously', async () => {
      const editVenueSpy = vi.spyOn(api, 'editVenue')

      renderForm({ ...baseVenue, openingHours: null })

      await userEvent.click(screen.getByText(/Enregistrer/))

      expect(editVenueSpy).toHaveBeenCalledWith({
        path: { venue_id: expect.anything() },
        body: expect.not.objectContaining({ openingHours: expect.anything() }),
      })
    })

    it('should send opening hours if the field was not filled, but the openingHours already existed', async () => {
      const editVenueSpy = vi.spyOn(api, 'editVenue')
      renderForm({
        ...baseVenue,
        openingHours: {
          MONDAY: [
            ['09:00', '12:00'],
            ['13:00', '18:00'],
          ],
          TUESDAY: [],
          WEDNESDAY: [],
          THURSDAY: [],
          FRIDAY: [],
          SATURDAY: [],
          SUNDAY: [],
        },
      })

      const morningOpen = document.querySelector<HTMLInputElement>(
        'input[name="openingHours.MONDAY.0.0"]'
      )!
      const morningClose = document.querySelector<HTMLInputElement>(
        'input[name="openingHours.MONDAY.0.1"]'
      )!
      const afternoonOpen = document.querySelector<HTMLInputElement>(
        'input[name="openingHours.MONDAY.1.0"]'
      )!
      const afternoonClose = document.querySelector<HTMLInputElement>(
        'input[name="openingHours.MONDAY.1.1"]'
      )!

      await userEvent.clear(morningOpen)
      await userEvent.type(morningOpen, '08:00')
      await userEvent.clear(morningClose)
      await userEvent.type(morningClose, '12:00')
      await userEvent.clear(afternoonOpen)
      await userEvent.type(afternoonOpen, '13:00')
      await userEvent.clear(afternoonClose)
      await userEvent.type(afternoonClose, '19:00')

      await userEvent.click(screen.getByText(/Enregistrer/))

      expect(editVenueSpy).toHaveBeenCalledWith({
        path: { venue_id: expect.anything() },
        body: expect.objectContaining({
          openingHours: expect.objectContaining({
            MONDAY: [
              ['08:00', '12:00'],
              ['13:00', '19:00'],
            ],
          }),
        }),
      })
    })

    it('should let the actor submit then when synchronized with acceslibre even if accessibility was never set', async () => {
      const editVenueSpy = vi.spyOn(api, 'editVenue')
      renderForm({
        ...baseVenue,
        audioDisabilityCompliant: null,
        motorDisabilityCompliant: null,
        mentalDisabilityCompliant: null,
        visualDisabilityCompliant: null,
        externalAccessibilityId: '666',
      })

      await userEvent.click(screen.getByText(/Enregistrer/))

      expect(editVenueSpy).toHaveBeenCalled()
    })

    it('should let the actor submit with volunteering url', async () => {
      const editVenueSpy = vi.spyOn(api, 'editVenue')
      renderForm({
        ...baseVenue,
      })

      expect(screen.getByText('Bénévolat')).toBeInTheDocument()

      await userEvent.type(
        screen.getByLabelText(/URL de votre page JeVeuxAider.gouv.fr/),
        'https://www.jeveuxaider.gouv.fr/organisations/exemple'
      )

      await userEvent.click(screen.getByText(/Enregistrer/))

      expect(editVenueSpy).toHaveBeenCalledWith({
        path: { venue_id: 1 },
        body: expect.objectContaining({
          volunteeringUrl:
            'https://www.jeveuxaider.gouv.fr/organisations/exemple',
        }),
      })
    })

    it('should log an event when the user submit an invalid volunteering url', async () => {
      vi.mocked(getVolunteeringUrlError).mockReturnValue('any-error')

      renderForm({ ...baseVenue })

      await userEvent.type(
        screen.getByLabelText(/URL de votre page JeVeuxAider.gouv.fr/),
        'any-url'
      )

      await userEvent.tab()

      expect(mockLogEvent).toHaveBeenCalledWith(
        Events.VENUE_FORM_VOLUNTEERING_URL_ERROR,
        {
          volunteeringUrl: 'any-url',
        }
      )
    })

    it('should not let the actor submit then when not synchronized with acceslibre if accessibility was never set', async () => {
      const editVenueSpy = vi.spyOn(api, 'editVenue')
      renderForm({
        ...baseVenue,
        audioDisabilityCompliant: null,
        motorDisabilityCompliant: null,
        mentalDisabilityCompliant: null,
        visualDisabilityCompliant: null,
        externalAccessibilityId: null,
      })

      await userEvent.click(screen.getByText(/Enregistrer/))
      expect(
        screen.getByText(
          'Veuillez sélectionner au moins un critère d’accessibilité'
        )
      ).toBeInTheDocument()
      expect(editVenueSpy).not.toHaveBeenCalled()
    })

    it('should display an accessibility section', async () => {
      renderForm({ ...baseVenue })

      await waitFor(() => {
        expect(
          screen.getByText('Modalités d’accessibilité')
        ).toBeInTheDocument()
      })
    })

    it('should render the withdrawal details section', async () => {
      renderForm({ ...baseVenue })

      expect(
        await screen.findByText('Informations de retrait de vos offres')
      ).toBeInTheDocument()
    })

    describe('when the venue is not permanent', () => {
      it('should not display any "Horaires d\'ouverture" section', async () => {
        renderForm({ ...baseVenue, isPermanent: false })

        await waitFor(() => {
          expect(
            screen.queryByText(/Horaires d'ouverture/)
          ).not.toBeInTheDocument()
        })
      })
    })

    describe('when the venue is not open to public', () => {
      it('should not display any "Addresse et horaires" subsection', async () => {
        renderForm({ ...baseVenue, isOpenToPublic: false })

        await waitFor(() => {
          expect(
            screen.queryByText('Adresse et horaires')
          ).not.toBeInTheDocument()
        })
      })

      it('should not display any accessibility subsection', async () => {
        renderForm({ ...baseVenue, isOpenToPublic: false })

        await waitFor(() => {
          expect(
            screen.queryByText('Modalités d’accessibilité')
          ).not.toBeInTheDocument()
        })
      })

      it('should not produce an error when accessibility is not filled nor externally defined on submit form', async () => {
        const editVenueSpy = vi.spyOn(api, 'editVenue')
        renderForm({
          ...baseVenue,
          audioDisabilityCompliant: null,
          mentalDisabilityCompliant: null,
          visualDisabilityCompliant: null,
          motorDisabilityCompliant: null,
          isOpenToPublic: false,
          activity: DisplayableActivity.FESTIVAL,
          collectiveDomains: [{ id: 1, name: 'FESTIVAL' }],
        })

        // If the user tries to submit the form without filling the accessibility section
        // no error should be displayed. We edit the description to trigger the form dirty state.
        await userEvent.type(screen.getByLabelText('Description'), '…')
        await userEvent.click(screen.getByText(/Enregistrer/))

        expect(editVenueSpy).toHaveBeenCalled()
      })
    })

    describe('when the venue is open to public', () => {
      it('should display an "Addresse et horaires" subsection', async () => {
        renderForm({ ...baseVenue, isOpenToPublic: true })

        await waitFor(() => {
          expect(screen.getByText('Adresse et horaires')).toBeInTheDocument()
        })
      })

      it('should display a mandatory accessibility subsection when internally defined', async () => {
        renderForm({ ...baseVenue, isOpenToPublic: true })

        await waitFor(() => {
          expect(
            screen.getByText('Modalités d’accessibilité')
          ).toBeInTheDocument()
          expect(
            screen.getByText(
              'Votre établissement est accessible au public en situation de handicap :'
            )
          ).toBeInTheDocument()
          expect(
            screen.getByText('Sélectionnez au moins une option')
          ).toBeInTheDocument()
        })
      })

      it('should produce an error when accessibility is neither filled nor externally defined on submit form', async () => {
        renderForm({
          ...baseVenue,
          audioDisabilityCompliant: null,
          mentalDisabilityCompliant: null,
          visualDisabilityCompliant: null,
          motorDisabilityCompliant: null,
          isOpenToPublic: true,
        })

        // If the user tries to submit the form without filling the accessibility section
        // an error should be displayed. We edit the description to trigger the form dirty state.
        await userEvent.type(screen.getByLabelText('Description'), '…')
        await userEvent.click(screen.getByText(/Enregistrer/))
        await waitFor(() => {
          expect(
            screen.getByText(
              'Veuillez sélectionner au moins un critère d’accessibilité'
            )
          ).toBeInTheDocument()
        })
      })

      it('should display an acceslibre accessibility subsection when externally defined', async () => {
        renderForm({
          ...baseVenue,
          isOpenToPublic: true,
          externalAccessibilityData: {
            isAccessibleAudioDisability: true,
            isAccessibleMentalDisability: false,
            isAccessibleMotorDisability: true,
            isAccessibleVisualDisability: true,
          },
        })

        await waitFor(() => {
          expect(
            screen.queryByText('Modalités d’accessibilité')
          ).not.toBeInTheDocument()
          expect(
            screen.getByText('Modalités d’accessibilité via acceslibre')
          ).toBeInTheDocument()
        })
      })
    })
  })
})
