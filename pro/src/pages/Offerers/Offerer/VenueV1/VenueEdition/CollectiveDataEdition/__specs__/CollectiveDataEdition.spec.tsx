import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { SENT_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import {
  domtomOptions,
  mainlandInterventionOption,
  mainlandOptions,
} from 'core/shared/interventionOptions'
import * as useNotification from 'hooks/useNotification'
import {
  defaultDMSApplicationForEAC,
  defaultGetVenue,
} from 'utils/collectiveApiFactories'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import {
  CollectiveDataEdition,
  CollectiveDataEditionProps,
} from '../CollectiveDataEdition'

// RomainC: we need this mock to accelerate this test
// it('should select (unselect) "Toute la France" and "France métropolitaine" when selecting (unselecting) all (one) departments'
// in which he is clicking on all departements one by one
// if we only mock mainlandOptions, the mock is not use to build venueInterventionOptions, allDepartmentValues and mainlandValues
// and the test fail...
// the workaround I found is to mock this way :
vi.mock('core/shared/interventionOptions', async () => {
  const originalModule = await vi.importActual<
    typeof import('core/shared/interventionOptions')
  >('core/shared/interventionOptions')

  const mockedMainlandOptions = [
    { value: '01', label: '01 - Ain' },
    { value: '02', label: '02 - Aisne' },
    { value: '03', label: '03 - Allier' },
    { value: '04', label: '04 - Alpes-de-Haute-Provence' },
    { value: '05', label: '05 - Hautes-Alpes' },
  ]

  return {
    __esModule: true,
    ...originalModule,
    mainlandOptions: mockedMainlandOptions,
    venueInterventionOptions: [
      {
        value: 'culturalPartner',
        label: 'Dans mon lieu',
      },
      originalModule.mainlandInterventionOption,
      ...mockedMainlandOptions,
      ...originalModule.domtomOptions,
    ],
    allDepartmentValues: [
      ...mockedMainlandOptions.map(({ value }) => value),
      ...originalModule.domtomOptions.map(({ value }) => value),
    ],
    mainlandValues: mockedMainlandOptions.map(({ value }) => value),
  }
})

const mockedUsedNavigate = vi.fn()
vi.mock('react-router-dom', async () => ({
  ...(await vi.importActual('react-router-dom')),
  useParams: () => ({
    offererId: 'O1',
    venueId: 'V1',
  }),
  useNavigate: () => mockedUsedNavigate,
}))

const renderCollectiveDataEdition = (
  props: Partial<CollectiveDataEditionProps> = {},
  options?: RenderWithProvidersOptions
) =>
  renderWithProviders(
    <CollectiveDataEdition
      venue={{ ...defaultGetVenue, hasAdageId: true }}
      {...props}
    />,
    { initialRouterEntries: ['/edition'], ...options }
  )

describe('CollectiveDataEdition', () => {
  const notifyErrorMock = vi.fn()
  const notifySuccessMock = vi.fn()

  beforeEach(() => {
    vi.spyOn(api, 'getVenuesEducationalStatuses').mockResolvedValue({
      statuses: [
        {
          id: 1,
          name: 'statut 1',
        },
        {
          id: 2,
          name: 'statut 2',
        },
      ],
    })
    vi.spyOn(api, 'listEducationalDomains').mockResolvedValue([
      { id: 1, name: 'domain 1' },
      { id: 2, name: 'domain 2' },
    ])
    vi.spyOn(api, 'getEducationalPartners').mockResolvedValue({ partners: [] })
    vi.spyOn(api, 'editVenueCollectiveData').mockResolvedValue({
      ...defaultGetVenue,
    })

    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      success: notifySuccessMock,
      error: notifyErrorMock,
      information: vi.fn(),
      pending: vi.fn(),
      close: vi.fn(),
    }))
  })

  describe('render', () => {
    it('should display read only information', async () => {
      renderCollectiveDataEdition({}, { initialRouterEntries: ['/'] })

      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      expect(screen.getByText('Référencé dans ADAGE')).toBeInTheDocument()
      expect(
        screen.getByText('Présentation pour les enseignants')
      ).toBeInTheDocument()
      expect(screen.getByText('Informations du lieu')).toBeInTheDocument()
      expect(screen.getByText('Contact')).toBeInTheDocument()
    })

    it('should render form without errors', async () => {
      renderCollectiveDataEdition()

      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      const descriptionField = screen.queryByLabelText(
        'Démarche d’éducation artistique et culturelle',
        { exact: false }
      )
      const studentsField = screen.getByLabelText(/Public cible/)
      const websiteField = screen.getByLabelText(/URL de votre site web/)
      const phoneField = screen.getByLabelText(/Numéro de téléphone/)
      const emailField = screen.getByLabelText(/Email/)
      const domainsField = screen.getByLabelText(
        /Domaine artistique et culturel/
      )
      const interventionAreaField = screen.getByLabelText(/Zone de mobilité/)
      const statusField = screen.getByLabelText(/Statut/)
      const culturalPartnersField = screen.getByLabelText(
        /Réseaux partenaires EAC/
      )

      expect(descriptionField).toBeInTheDocument()
      expect(studentsField).toBeInTheDocument()
      expect(websiteField).toBeInTheDocument()
      expect(phoneField).toBeInTheDocument()
      expect(emailField).toBeInTheDocument()
      expect(domainsField).toBeInTheDocument()
      expect(interventionAreaField).toBeInTheDocument()
      expect(statusField).toBeInTheDocument()
      expect(culturalPartnersField).toBeInTheDocument()
    })

    it('should display dms timeline if venue has dms application and ff active', async () => {
      renderCollectiveDataEdition({
        venue: {
          ...defaultGetVenue,
          id: 1,
          hasAdageId: false,
          collectiveDmsApplications: [{ ...defaultDMSApplicationForEAC }],
        },
      })

      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      await waitFor(() => {
        expect(
          screen.getByText('Votre dossier a été déposé')
        ).toBeInTheDocument()
      })
    })

    it('should display popin when user is leaving page without saving', async () => {
      renderCollectiveDataEdition()

      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      const phoneField = screen.getByLabelText(/Numéro de téléphone/)
      await userEvent.type(phoneField, '0612345678')
      await userEvent.click(screen.getByText('Annuler et quitter'))

      await waitFor(() =>
        expect(
          screen.getByText('Les informations non enregistrées seront perdues')
        ).toBeInTheDocument()
      )
    })
  })

  describe('error fields', () => {
    it('should display error fields', async () => {
      renderCollectiveDataEdition()

      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      const websiteField = screen.getByLabelText(/URL de votre site web/)
      const phoneField = screen.getByLabelText(/Numéro de téléphone/)
      const emailField = screen.getByLabelText(/Email/)
      const title = screen.getByText('Présentation pour les enseignants')

      await userEvent.type(websiteField, 'wrong url')
      await userEvent.type(phoneField, 'not a valid phone')
      await userEvent.type(emailField, 'not a valid email')

      await userEvent.click(title)

      expect(
        screen.queryByText(
          'Veuillez entrer un numéro de téléphone valide, exemple : 612345678'
        )
      ).toBeInTheDocument()
      expect(
        screen.queryByText(
          'Veuillez renseigner une URL valide. Ex : https://exemple.com'
        )
      ).toBeInTheDocument()
      expect(
        screen.queryByText(
          'Veuillez renseigner un email valide, exemple : mail@exemple.com'
        )
      ).toBeInTheDocument()
    })

    it('should not display error fields when fields are valid', async () => {
      renderCollectiveDataEdition()

      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      const websiteField = screen.getByLabelText(/URL de votre site web/)
      const phoneField = screen.getByLabelText(/Numéro de téléphone/)
      const emailField = screen.getByLabelText(/Email/)
      const title = screen.getByText('Présentation pour les enseignants')

      await userEvent.type(websiteField, 'https://mon-site.com')
      await userEvent.type(phoneField, '0600000000')
      await userEvent.type(emailField, 'email@domain.com')

      await userEvent.click(title)

      await waitFor(() =>
        expect(
          screen.queryByText('Veuillez renseigner un email valide')
        ).not.toBeInTheDocument()
      )
      expect(
        screen.queryByText(
          'Veuillez entrer un numéro de téléphone valide, exemple : 612345678'
        )
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText(
          'Veuillez renseigner une URL valide. Ex : https://exemple.com'
        )
      ).not.toBeInTheDocument()
    })

    it('should not display error fields when fields are empty', async () => {
      renderCollectiveDataEdition()

      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      const websiteField = screen.getByLabelText(/URL de votre site web/)
      const phoneField = screen.getByLabelText(/Numéro de téléphone/)
      const emailField = screen.getByLabelText(/Email/)
      const title = screen.getByText('Présentation pour les enseignants')

      await userEvent.click(websiteField)
      await userEvent.click(phoneField)
      await userEvent.click(emailField)
      await userEvent.click(title)

      await waitFor(() =>
        expect(
          screen.queryByText('Veuillez renseigner un email valide')
        ).not.toBeInTheDocument()
      )
      expect(
        screen.queryByText(
          'Veuillez entrer un numéro de téléphone valide, exemple : 612345678'
        )
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText(
          'Veuillez renseigner une URL valide. Ex : https://exemple.com'
        )
      ).not.toBeInTheDocument()
    })
  })

  describe('intervention area', () => {
    it('should select all mainland departments when clicking on "France métropolitaine"', async () => {
      renderCollectiveDataEdition()

      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      const interventionAreaField = screen.getByLabelText(/Zone de mobilité/)
      await userEvent.click(interventionAreaField)
      await waitFor(() =>
        expect(
          screen.queryByRole('option', {
            name: mainlandInterventionOption.label,
          })
        ).toBeInTheDocument()
      )
      const mainlandOption = screen.getByLabelText(
        mainlandInterventionOption.label
      )
      await userEvent.click(mainlandOption)
      ;[...mainlandOptions].forEach((option) => {
        expect(screen.getByLabelText(option.label)).toBeChecked()
      })
    })

    it('should select only domtom options', async () => {
      renderCollectiveDataEdition()

      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      const interventionAreaField = screen.getByLabelText(/Zone de mobilité/)
      await userEvent.click(interventionAreaField)
      await waitFor(() =>
        expect(
          screen.getByLabelText(mainlandOptions[0]!.label)
        ).not.toBeChecked()
      )
      for await (const option of domtomOptions) {
        await userEvent.click(screen.getByLabelText(option.label))
      }
      domtomOptions.forEach((option) =>
        expect(screen.getByLabelText(option.label)).toBeChecked()
      )
    })

    it('should select (unselect) "France métropolitaine" when selecting (unselecting) all (one) departments', async () => {
      renderCollectiveDataEdition()

      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      const interventionAreaField = screen.getByLabelText(/Zone de mobilité/)
      await userEvent.click(interventionAreaField)

      const mainlandOption = screen.getByRole('checkbox', {
        name: 'France métropolitaine',
      })
      expect(mainlandOption).toBeInTheDocument()

      // check all mainland options
      for await (const option of mainlandOptions) {
        await userEvent.click(
          screen.getByRole('checkbox', { name: option.label })
        )
      }

      expect(mainlandOption).toBeChecked()

      // check all other departments
      for await (const option of domtomOptions) {
        await userEvent.click(screen.getByLabelText(option.label))
      }

      await userEvent.click(screen.getByLabelText(mainlandOptions[0]!.label))
      expect(
        screen.getByRole('option', { name: 'France métropolitaine' })
      ).not.toBeChecked()
    })
  })

  describe('submit', () => {
    it('should display error toast when adapter call failed', async () => {
      vi.spyOn(api, 'editVenueCollectiveData').mockRejectedValueOnce(
        new ApiError({} as ApiRequestOptions, { status: 500 } as ApiResult, '')
      )
      renderCollectiveDataEdition()
      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      const emailField = screen.getByLabelText(/Email/)
      await userEvent.type(emailField, 'email@domain.com')

      const submitButton = screen.getByRole('button', {
        name: 'Enregistrer et quitter',
      })
      expect(submitButton).not.toBeDisabled()
      await userEvent.click(submitButton)

      await waitFor(() =>
        expect(notifyErrorMock).toHaveBeenCalledWith(SENT_DATA_ERROR_MESSAGE)
      )
    })
  })

  it('shoud redirect to venue edition page with state', async () => {
    renderCollectiveDataEdition()
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    const emailField = screen.getByLabelText(/Email/)
    await userEvent.type(emailField, 'email@domain.com')

    const submitButton = screen.getByRole('button', {
      name: 'Enregistrer et quitter',
    })
    await userEvent.click(submitButton)

    expect(mockedUsedNavigate).toHaveBeenCalledWith(
      '/structures/1/lieux/1/collectif'
    )
  })

  describe('prefill', () => {
    it('should prefill form with venue collective data', async () => {
      renderCollectiveDataEdition({
        venue: {
          ...defaultGetVenue,
          hasAdageId: true,
          collectiveDomains: [{ id: 1, name: 'domain 1' }],
          collectiveDescription: '',
          collectiveEmail: 'toto@domain.com',
          collectiveInterventionArea: [],
          collectiveLegalStatus: { id: 1, name: 'statut 1' },
          collectiveNetwork: [],
          collectivePhone: '',
          collectiveStudents: [],
          collectiveWebsite: '',
          siret: '1234567890',
        },
      })

      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

      const emailField = screen.getByLabelText(/Email/)

      const statusField = screen.getByLabelText(/Statut/)

      expect(emailField).toHaveValue('toto@domain.com')
      expect(statusField).toHaveValue('1')

      await userEvent.click(
        await screen.findByLabelText(/Domaine artistique et culturel */)
      )
      await waitFor(async () =>
        expect(
          await screen.findAllByRole('checkbox', { checked: true })
        ).toHaveLength(1)
      )
    })

    it('should not call educational partner if venue has no siret and no collective data', async () => {
      renderCollectiveDataEdition()

      await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
    })
  })
})
