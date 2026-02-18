import { screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Route, Routes } from 'react-router'
import useSWR, { type SWRResponse } from 'swr'
import { expect, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import * as apiAdresse from '@/apiClient/adresse/apiAdresse'
import { api } from '@/apiClient/api'
import { ApiError, type GetVenueResponseModel } from '@/apiClient/v1'
import type { ApiRequestOptions } from '@/apiClient/v1/core/ApiRequestOptions'
import type { ApiResult } from '@/apiClient/v1/core/ApiResult'
import * as useEducationalDomains from '@/commons/hooks/swr/useEducationalDomains'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { VenueEditionFormScreen } from './VenueEditionFormScreen'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

function renderForm(
  venue: GetVenueResponseModel,
  options?: RenderWithProvidersOptions
) {
  const Wrapper = () => {
    return <VenueEditionFormScreen venue={venue} />
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
    options
  )
}

vi.mock('@/apiClient/api', () => ({
  api: {
    postCreateVenue: vi.fn(),
    getSiretInfo: vi.fn(),
    editVenue: vi.fn(),
    getAvailableReimbursementPoints: vi.fn(() => Promise.resolve([])),
    canOffererCreateEducationalOffer: vi.fn(),
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

const baseVenue: GetVenueResponseModel = {
  ...defaultGetVenue,
  isPermanent: true,
}

describe('VenueEditionFormScreen', () => {
  const useSWRMock = vi.mocked(useSWR)

  beforeEach(() => {
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

  it('should mention "structure" instead of "lieu"', () => {
    renderForm({ ...baseVenue, isVirtual: true })

    expect(
      screen.getByText(
        /Cette structure vous permet uniquement de créer des offres numériques, elle/
      )
    ).toBeInTheDocument()
  })

  describe('on readonly (VenueEditionReadOnly)', () => {
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
      expect(await screen.findByText('Vos informations')).toBeInTheDocument()
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

    it('should dispaly an accessibility section', () => {
      renderForm(baseVenue, { initialRouterEntries: ['/'] })

      expect(screen.getByText('Modalités d’accessibilité')).toBeInTheDocument()
    })

    it('should display the acceslibre section as an accessibility section when accessibility is externally defined', () => {
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

    it('should always display an "Accueil du public"', () => {
      renderForm(baseVenue, {
        initialRouterEntries: ['/'],
      })
      expect(screen.getByText('Accueil du public')).toBeInTheDocument()
    })

    describe('when the venue is not open to public', () => {
      it('should not display any address and hours subsection', () => {
        renderForm(
          { ...baseVenue, isOpenToPublic: false },
          {
            initialRouterEntries: ['/'],
          }
        )

        expect(
          screen.queryByText('Adresse et horaires')
        ).not.toBeInTheDocument()
      })

      it('should not display any accessibility subsection', () => {
        renderForm(
          { ...baseVenue, isOpenToPublic: false },
          {
            initialRouterEntries: ['/'],
          }
        )

        expect(
          screen.queryByText(/Modalités d’accessibilité/)
        ).not.toBeInTheDocument()
      })

      it('should display a message indicating the venue is not open to public', () => {
        renderForm(
          { ...baseVenue, isOpenToPublic: false },
          {
            initialRouterEntries: ['/'],
          }
        )

        expect(
          screen.getByText('Accueil du public dans la structure : Non')
        ).toBeInTheDocument()
      })
    })

    describe('when the venue is open to public', () => {
      it('should display an "Addresse et horaires" subsection', () => {
        renderForm(
          { ...baseVenue, isOpenToPublic: true },
          {
            initialRouterEntries: ['/'],
          }
        )

        expect(screen.getByText('Adresse et horaires')).toBeInTheDocument()
      })

      it('should display an accessibility subsection', () => {
        renderForm(
          { ...baseVenue, isOpenToPublic: true },
          {
            initialRouterEntries: ['/'],
          }
        )
        expect(
          screen.queryByText(/Modalités d’accessibilité/)
        ).toBeInTheDocument()
      })

      it('should display the acceslibre section as an accessibility sub section when accessibility is externally defined', () => {
        renderForm(
          {
            ...baseVenue,
            isOpenToPublic: true,
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
    })
  })

  // See VenueEdition.spec.tsx for additional tests.
  describe('on edition (VenueEditionForm)', () => {
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

      await userEvent.click(screen.getByText(/Enregistrer/))

      expect(editVenueSpy).toHaveBeenCalledWith(
        expect.anything(),
        expect.not.objectContaining({ openingHours: expect.anything() })
      )
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
        },
      })

      const mondayGroup = await screen.findByRole('group', {
        name: /Lundi/,
      })

      const [morningOpen, afternoonOpen] =
        await within(mondayGroup).findAllByLabelText(/Ouvre à/)
      const [morningClose, afternoonClose] =
        await within(mondayGroup).findAllByLabelText(/Ferme à/)

      await userEvent.clear(morningOpen)
      await userEvent.type(morningOpen, '08:00')
      await userEvent.clear(morningClose)
      await userEvent.type(morningClose, '12:00')
      await userEvent.clear(afternoonOpen)
      await userEvent.type(afternoonOpen, '13:00')
      await userEvent.clear(afternoonClose)
      await userEvent.type(afternoonClose, '19:00')

      await userEvent.click(screen.getByText(/Enregistrer/))

      expect(editVenueSpy).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({
          openingHours: expect.objectContaining({
            MONDAY: [
              ['08:00', '12:00'],
              ['13:00', '19:00'],
            ],
          }),
        })
      )
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
          expect(
            screen.queryByTestId('wrapper-publicName')
          ).not.toBeInTheDocument()
        })

        expect(
          screen.queryByTestId('wrapper-description')
        ).not.toBeInTheDocument()
        expect(
          screen.queryByText('Accessibilité du lieu')
        ).not.toBeInTheDocument()
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

    it('should display an "Accueil du public section"', async () => {
      renderForm(baseVenue)

      await waitFor(() => {
        expect(screen.getByText('Accueil du public')).toBeInTheDocument
      })
    })

    it('should display a mandatory toggle to define isOpenToPublic', async () => {
      renderForm({ ...baseVenue, isOpenToPublic: false })

      const toggle = screen.getByRole('group', {
        name: 'Accueillez-vous du public dans votre structure ?',
      })

      await waitFor(() => {
        expect(toggle).toBeInTheDocument()
      })
    })

    it('should pass the isOpenToPublic value to the API', async () => {
      const editVenueSpy = vi.spyOn(api, 'editVenue')

      renderForm({
        ...baseVenue,
        isOpenToPublic: false,
      })

      await userEvent.click(screen.getByRole('radio', { name: 'Oui' }))
      await userEvent.selectOptions(
        screen.getByRole('combobox', { name: /Activité principale/ }),
        screen.getByRole('option', {
          name: 'Centre culturel pluridisciplinaire',
        })
      )
      await userEvent.click(screen.getByText(/Enregistrer/))

      expect(editVenueSpy).toHaveBeenCalledWith(
        expect.anything(),
        expect.objectContaining({ isOpenToPublic: true })
      )
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
          collectiveDomains: [{ id: 1, name: 'FESTIVAL' }],
        })

        // If the user tries to submit the form without filling the accessibility section
        // no error should be displayed. We edit the description to trigger the form dirty state.
        await userEvent.type(screen.getByLabelText('Description'), '…')
        await userEvent.click(screen.getByText(/Enregistrer/))

        expect(editVenueSpy).toHaveBeenCalled()
      })

      it('should display the proper activities list for structures not open to public', async () => {
        renderForm({
          ...baseVenue,
          isOpenToPublic: false,
        })

        const mainActivitySelect = await screen.findByRole('combobox', {
          name: /Activité principale/,
        })

        ;[
          'Société de production, tourneur ou label',
          'Presse ou média',
          'Cinéma itinérant',
        ].forEach((label) => {
          expect(
            within(mainActivitySelect).getByRole('option', { name: label })
          ).toBeInTheDocument()
        })
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

      it('should display the activity select', async () => {
        renderForm({
          ...baseVenue,
          isOpenToPublic: true,
          activity: null,
        })

        const activitySelect =
          await screen.findByLabelText(/Activité principale/)

        expect(activitySelect).toBeInTheDocument()
        expect(activitySelect).toHaveValue('')
        expect(
          screen.getByText('Sélectionnez votre activité principale')
        ).toBeInTheDocument()
        expect(activitySelect).not.toBeDisabled()
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

      it('should display the proper activities list for structures open to public', async () => {
        renderForm({ ...baseVenue, isOpenToPublic: true })

        const mainActivitySelect = await screen.findByRole('combobox', {
          name: /Activité principale/,
        })

        ;['Librairie', 'Cinéma', 'Centre socio-culturel'].forEach((label) => {
          expect(
            within(mainActivitySelect).getByRole('option', { name: label })
          ).toBeInTheDocument()
        })
      })
    })

    describe('when days/hours or accessibility have been updated', () => {
      it('should be reset to initial values if user set isOpenToPublic to false', async () => {
        renderForm({ ...baseVenue, isOpenToPublic: true })
        expect(baseVenue.motorDisabilityCompliant).toBe(false)
        let visualAccessibilityCheckbox = screen.getByRole('checkbox', {
          name: 'Moteur',
        })
        await userEvent.click(visualAccessibilityCheckbox)
        expect(visualAccessibilityCheckbox).toBeChecked()
        const noRadio = await screen.findByRole('radio', { name: 'Non' })
        await userEvent.click(noRadio)
        const yesRadio = await screen.findByRole('radio', { name: 'Oui' })
        await userEvent.click(yesRadio)
        visualAccessibilityCheckbox = screen.getByRole('checkbox', {
          name: 'Moteur',
        })
        expect(visualAccessibilityCheckbox).not.toBeChecked()
      })
    })
  })
  describe('Cultural domains', () => {
    beforeEach(() => {
      useSWRMock.mockReturnValue({
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
      } as SWRResponse)
    })

    it('should display about activity at top with the FF enabled', () => {
      renderForm(
        {
          ...baseVenue,
          description: 'TOTOTO',
          contact: {
            phoneNumber: '123',
            email: 'e@mail.fr',
            website: 'site.web',
          },
          collectiveDomains: [
            { id: 1, name: 'domaine 1' },
            { id: 3, name: 'domaine III' },
          ],
        },
        {
          initialRouterEntries: ['/'],
        }
      )
      const h3Titles = screen.getAllByRole('heading', { level: 3 })
      expect(h3Titles).toHaveLength(3)
      expect(h3Titles[1].textContent).toEqual('À propos de votre activité')
      expect(screen.getByText(/Domaine\(s\) d’activité/)).toBeInTheDocument()
      expect(screen.getByText(/domaine 1, domaine III/)).toBeInTheDocument()
    })

    it('should display no domain if not present', () => {
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
        {
          initialRouterEntries: ['/'],
        }
      )
      expect(screen.getByText(/Non renseigné/)).toBeInTheDocument()
    })

    it('should render cultural domains input', async () => {
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
        {
          initialRouterEntries: ['/edition'],
        }
      )
      const multiSelect = screen.getByLabelText(
        'Sélectionnez un ou plusieurs domaines d’activité'
      )

      expect(multiSelect).toBeInTheDocument()
      await userEvent.click(multiSelect)
      await waitFor(() => {
        expect(screen.getByTestId('panel-scrollable')).toBeInTheDocument()
      })
      expect(screen.getByText(/3 résultats trouvés/)).toBeInTheDocument()
      expect(screen.getByText(/domaine III/)).toBeInTheDocument()
    })

    it('should render cultural domains input with context value', async () => {
      renderForm(
        {
          ...baseVenue,
          description: 'TOTOTO',
          contact: {
            phoneNumber: '123',
            email: 'e@mail.fr',
            website: 'site.web',
          },
          collectiveDomains: [{ name: 'domaine 1', id: 1 }],
        },
        {
          initialRouterEntries: ['/edition'],
        }
      )

      await userEvent.click(screen.getByLabelText('domaine sélectionné'))
      await waitFor(() => {
        expect(screen.getByTestId('panel-scrollable')).toBeInTheDocument()
      })
      expect(screen.getAllByText(/domaine 1/)).toHaveLength(2)
    })

    it('should select cultural domain', async () => {
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
        {
          initialRouterEntries: ['/edition'],
        }
      )

      await userEvent.click(
        screen.getByLabelText(
          'Sélectionnez un ou plusieurs domaines d’activité'
        )
      )
      await waitFor(() => {
        expect(screen.getByTestId('panel-scrollable')).toBeInTheDocument()
      })
      expect(screen.getAllByText(/domaine 1/)).toHaveLength(1)
      await userEvent.click(screen.getByText(/domaine 1/))
      expect(screen.getAllByText(/domaine 1/)).toHaveLength(2)
      await userEvent.click(screen.getByText(/domaine III/))
      expect(screen.getByLabelText('domaines sélectionnés')).toBeInTheDocument()
    })
  })
})
