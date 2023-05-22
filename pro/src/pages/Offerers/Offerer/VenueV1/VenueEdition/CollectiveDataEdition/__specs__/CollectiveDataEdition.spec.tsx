import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { ApiError, GetVenueResponseModel } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { domtomOptions, mainlandOptions } from 'core/shared/interventionOptions'
import * as useNotification from 'hooks/useNotification'
import {
  collectiveCategoryFactory,
  collectiveSubCategoryFactory,
  venueCollectiveDataFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveDataEdition from '../CollectiveDataEdition'

// RomainC: we need this mock to accelerate this test
// it('should select (unselect) "Toute la France" and "France métropolitaine" when selecting (unselecting) all (one) departments'
// in which he is clicking on all departements one by one
// if we only mock mainlandOptions, the mock is not use to build venueInterventionOptions, allDepartmentValues and mainlandValues
// and the test fail...
// the workaround I found is to mock this way :
jest.mock('core/shared/interventionOptions', () => {
  const originalModule = jest.requireActual<
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
        value: originalModule.CULTURAL_PARTNER_OPTION_VALUE,
        label: originalModule.CULTURAL_PARTNER_OPTION_LABEL,
      },
      ...originalModule.otherInterventionOptions,
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

jest.mock('apiClient/api', () => ({
  api: {
    getVenuesEducationalStatuses: jest.fn(),
    getEducationalPartners: jest.fn(),
    editVenueCollectiveData: jest.fn(),
    getVenueCollectiveData: jest.fn(),
    getEducationalPartner: jest.fn(),
    listEducationalDomains: jest.fn(),
    getCategories: jest.fn(),
  },
}))
const mockedUsedNavigate = jest.fn()
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    offererId: 'O1',
    venueId: 'V1',
  }),
  useNavigate: () => mockedUsedNavigate,
}))

jest.mock('hooks/useNotification')

const waitForLoader = () =>
  waitFor(() => {
    expect(screen.getByLabelText(/E-mail/)).toBeInTheDocument()
  })

const renderCollectiveDataEdition = () =>
  renderWithProviders(<CollectiveDataEdition />)

describe('CollectiveDataEdition', () => {
  const notifyErrorMock = jest.fn()
  const notifySuccessMock = jest.fn()

  beforeAll(() => {
    jest.spyOn(api, 'getVenuesEducationalStatuses').mockResolvedValue({
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
    jest.spyOn(api, 'listEducationalDomains').mockResolvedValue([
      { id: 1, name: 'domain 1' },
      { id: 2, name: 'domain 2' },
    ])
    jest
      .spyOn(api, 'getEducationalPartners')
      .mockResolvedValue({ partners: [] })
    jest
      .spyOn(api, 'editVenueCollectiveData')
      .mockResolvedValue({ id: 'A1' } as GetVenueResponseModel)

    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      success: notifySuccessMock,
      error: notifyErrorMock,
      information: jest.fn(),
      pending: jest.fn(),
      close: jest.fn(),
    }))

    jest.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [collectiveCategoryFactory(), collectiveCategoryFactory()],
      subcategories: [
        collectiveSubCategoryFactory({ categoryId: 'CATEGORY_1' }),
        collectiveSubCategoryFactory({ categoryId: 'CATEGORY_1' }),
        collectiveSubCategoryFactory({ categoryId: 'CATEGORY_2' }),
      ],
    })

    jest
      .spyOn(api, 'getVenueCollectiveData')
      .mockResolvedValue(venueCollectiveDataFactory())

    jest.spyOn(api, 'getEducationalPartner').mockRejectedValue({})
  })

  describe('render', () => {
    it('should render a loader while data is loading', async () => {
      renderCollectiveDataEdition()

      expect(screen.getByText(/Chargement en cours/)).toBeInTheDocument()
      await waitForLoader()
    })

    it('should render form without errors', async () => {
      renderCollectiveDataEdition()

      await waitForLoader()

      const descriptionField = screen.queryByLabelText(
        'Démarche d’éducation artistique et culturelle',
        { exact: false }
      )
      const studentsField = screen.getByLabelText(/Public cible/)
      const websiteField = screen.getByLabelText(/URL de votre site web/)
      const phoneField = screen.getByLabelText(/Numéro de téléphone/)
      const emailField = screen.getByLabelText(/E-mail/)
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

    it('should display toaster when some data could not be loaded', async () => {
      jest
        .spyOn(api, 'getVenuesEducationalStatuses')
        .mockRejectedValueOnce(
          new ApiError(
            {} as ApiRequestOptions,
            { status: 500 } as ApiResult,
            ''
          )
        )

      renderCollectiveDataEdition()
      await waitForLoader()

      await waitFor(() => {
        expect(notifyErrorMock).toHaveBeenCalledWith(GET_DATA_ERROR_MESSAGE)
      })
    })

    it('should display popin when user is leaving page without saving', async () => {
      renderCollectiveDataEdition()

      await waitForLoader()

      const phoneField = screen.getByLabelText(/Numéro de téléphone/)
      await userEvent.type(phoneField, '0612345678')
      await userEvent.click(screen.getByText('Retour page lieu'))

      await waitFor(() =>
        expect(
          screen.getByText(
            'Voulez vous quitter la page d’informations pour les enseignants ?'
          )
        ).toBeInTheDocument()
      )
    })
  })

  describe('error fields', () => {
    it('should display error fields', async () => {
      renderCollectiveDataEdition()

      await waitForLoader()

      const websiteField = screen.getByLabelText(/URL de votre site web/)
      const phoneField = screen.getByLabelText(/Numéro de téléphone/)
      const emailField = screen.getByLabelText(/E-mail/)
      const title = screen.getByText('Présentation pour les enseignants')

      await userEvent.type(websiteField, 'wrong url')
      await userEvent.type(phoneField, 'not a valid phone')
      await userEvent.type(emailField, 'not a valid email')

      await userEvent.click(title)

      expect(
        screen.queryByText('Veuillez entrer un numéro de téléphone valide')
      ).toBeInTheDocument()
      expect(
        screen.queryByText(
          'Veuillez renseigner une URL valide. Ex : https://exemple.com'
        )
      ).toBeInTheDocument()
      expect(
        screen.queryByText('Veuillez renseigner un e-mail valide')
      ).toBeInTheDocument()
    })

    it('should not display error fields when fields are valid', async () => {
      renderCollectiveDataEdition()

      await waitForLoader()

      const websiteField = screen.getByLabelText(/URL de votre site web/)
      const phoneField = screen.getByLabelText(/Numéro de téléphone/)
      const emailField = screen.getByLabelText(/E-mail/)
      const title = screen.getByText('Présentation pour les enseignants')

      await userEvent.type(websiteField, 'https://mon-site.com')
      await userEvent.type(phoneField, '0600000000')
      await userEvent.type(emailField, 'email@domain.com')

      await userEvent.click(title)

      await waitFor(() =>
        expect(
          screen.queryByText('Veuillez renseigner un e-mail valide')
        ).not.toBeInTheDocument()
      )
      expect(
        screen.queryByText('Veuillez entrer un numéro de téléphone valide')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText(
          'Veuillez renseigner une URL valide. Ex : https://exemple.com'
        )
      ).not.toBeInTheDocument()
    })

    it('should not display error fields when fields are empty', async () => {
      renderCollectiveDataEdition()

      await waitForLoader()

      const websiteField = screen.getByLabelText(/URL de votre site web/)
      const phoneField = screen.getByLabelText(/Numéro de téléphone/)
      const emailField = screen.getByLabelText(/E-mail/)
      const title = screen.getByText('Présentation pour les enseignants')

      await userEvent.click(websiteField)
      await userEvent.click(phoneField)
      await userEvent.click(emailField)
      await userEvent.click(title)

      await waitFor(() =>
        expect(
          screen.queryByText('Veuillez renseigner un e-mail valide')
        ).not.toBeInTheDocument()
      )
      expect(
        screen.queryByText('Veuillez entrer un numéro de téléphone valide')
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

      await waitForLoader()

      const interventionAreaField = screen.getByLabelText(/Zone de mobilité/)
      await userEvent.click(interventionAreaField)
      await waitFor(() =>
        expect(screen.queryByText('France métropolitaine')).toBeInTheDocument()
      )
      const mainlandOption = screen.getByLabelText('France métropolitaine')
      await userEvent.click(mainlandOption)
      ;[...mainlandOptions].forEach(option => {
        expect(screen.getByLabelText(option.label)).toBeChecked()
      })
    })

    it('should select only domtom options', async () => {
      renderCollectiveDataEdition()

      await waitForLoader()

      const interventionAreaField = screen.getByLabelText(/Zone de mobilité/)
      await userEvent.click(interventionAreaField)
      await waitFor(() =>
        expect(
          screen.getByLabelText(mainlandOptions[0].label)
        ).not.toBeChecked()
      )
      for await (const option of domtomOptions) {
        await userEvent.click(screen.getByLabelText(option.label))
      }
      domtomOptions.forEach(option =>
        expect(screen.getByLabelText(option.label)).toBeChecked()
      )
    })

    it('should select (unselect) "France métropolitaine" when selecting (unselecting) all (one) departments', async () => {
      renderCollectiveDataEdition()

      await waitForLoader()

      const interventionAreaField = screen.getByLabelText(/Zone de mobilité/)
      await userEvent.click(interventionAreaField)

      const mainlandOption = await screen.findByLabelText(
        'France métropolitaine'
      )
      expect(mainlandOption).toBeInTheDocument()

      // check all mainland options
      for await (const option of mainlandOptions) {
        await userEvent.click(screen.getByLabelText(option.label))
      }

      expect(mainlandOption).toBeChecked()

      // check all other departments
      for await (const option of domtomOptions) {
        await userEvent.click(screen.getByLabelText(option.label))
      }

      await userEvent.click(screen.getByLabelText(mainlandOptions[0].label))
      expect(screen.getByLabelText('France métropolitaine')).not.toBeChecked()
    })
  })

  describe('categories', () => {
    it('should prefill field with selected category and subcategory', async () => {
      jest.spyOn(api, 'getVenueCollectiveData').mockResolvedValueOnce(
        venueCollectiveDataFactory({
          collectiveEmail: 'test@example.com',
          collectiveSubCategoryId: 'SUB_CATEGORY_1',
        })
      )
      renderCollectiveDataEdition()
      await waitForLoader()

      const categoryField = screen.getByLabelText(/Catégorie/)
      const subCategoryField = screen.getByLabelText(/Sous-catégorie/)

      expect(categoryField).toHaveValue('CATEGORY_1')
      expect(subCategoryField).toHaveValue('SUB_CATEGORY_1')
    })

    it('should not display subcategory field if no category selected', async () => {
      jest.spyOn(api, 'getCategories').mockResolvedValueOnce({
        categories: [],
        subcategories: [],
      })
      renderCollectiveDataEdition()
      await waitForLoader()

      const subCategoryField = screen.queryByLabelText(/Sous-catégorie/)

      expect(subCategoryField).not.toBeInTheDocument()
    })

    it('should display subcategory field when category is selected', async () => {
      renderCollectiveDataEdition()
      await waitForLoader()

      const categoryField = screen.getByLabelText(/Catégorie/)
      await userEvent.selectOptions(categoryField, 'CATEGORY_2')

      const subCategoryField = screen.getByLabelText(/Sous-catégorie/)
      expect(subCategoryField).toBeInTheDocument()
    })
  })

  describe('submit', () => {
    it('should display error toast when adapter call failed', async () => {
      jest
        .spyOn(api, 'editVenueCollectiveData')
        .mockRejectedValueOnce(
          new ApiError(
            {} as ApiRequestOptions,
            { status: 500 } as ApiResult,
            ''
          )
        )
      renderCollectiveDataEdition()
      await waitForLoader()

      const emailField = screen.getByLabelText(/E-mail/)
      await userEvent.type(emailField, 'email@domain.com')

      const submitButton = screen.getByRole('button', { name: 'Enregistrer' })
      expect(submitButton).not.toBeDisabled()
      await userEvent.click(submitButton)

      await waitFor(() =>
        expect(notifyErrorMock).toHaveBeenCalledWith(
          'Une erreur est survenue lors de l’enregistrement des données'
        )
      )
    })
  })

  it('shoud redirect to venue edition page with state', async () => {
    renderCollectiveDataEdition()
    await waitForLoader()

    const emailField = screen.getByLabelText(/E-mail/)
    await userEvent.type(emailField, 'email@domain.com')

    const submitButton = screen.getByRole('button', { name: 'Enregistrer' })
    await userEvent.click(submitButton)

    expect(mockedUsedNavigate).toHaveBeenCalledWith('/structures/O1/lieux/V1', {
      state: {
        collectiveDataEditionSuccess:
          'Vos informations ont bien été enregistrées',
        scrollToElementId: 'venue-collective-data',
      },
    })
  })

  describe('prefill', () => {
    it('should prefill form with venue collective data', async () => {
      jest.spyOn(api, 'getVenueCollectiveData').mockResolvedValue({
        id: 'A1',
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
      })

      renderCollectiveDataEdition()

      await waitForLoader()

      const emailField = screen.getByLabelText(/E-mail/)

      const statusField = screen.getByLabelText(/Statut/)

      expect(emailField).toHaveValue('toto@domain.com')
      expect(statusField).toHaveValue('1')

      await userEvent.click(
        await screen.findByLabelText(/Domaine artistique et culturel/)
      )
      await waitFor(async () =>
        expect(
          await screen.findAllByRole('checkbox', { checked: true })
        ).toHaveLength(1)
      )

      expect(api.getEducationalPartner).not.toHaveBeenCalled()
    })

    it('should prefill form with educational partner data when venue has no collectiva data', async () => {
      jest.spyOn(api, 'getEducationalPartner').mockResolvedValueOnce({
        id: 1,
        siteWeb: 'http://monsite.com',
        statutId: 2,
        domaineIds: [1, 2],
      })
      jest
        .spyOn(api, 'getVenueCollectiveData')
        .mockResolvedValue(venueCollectiveDataFactory())

      renderCollectiveDataEdition()

      await waitForLoader()

      const websiteField = screen.getByLabelText(/URL de votre site web/)
      const statusField = screen.getByLabelText(/Statut/)
      const domainsInput = screen.getByLabelText(
        /Domaine artistique et culturel/
      )

      await waitFor(() => {
        expect(websiteField).toHaveValue('http://monsite.com')
      })
      expect(statusField).toHaveValue('2')

      await userEvent.click(domainsInput)
      await waitFor(() => {
        expect(screen.getAllByRole('checkbox', { checked: true })).toHaveLength(
          2
        )
      })

      expect(api.getEducationalPartner).toHaveBeenCalledWith('1234567890')
      expect(screen.getByRole('button', { name: 'Enregistrer' })).toBeEnabled()
    })

    it('should not call educational partner if venue has no siret and no collective data', async () => {
      jest.spyOn(api, 'getVenueCollectiveData').mockResolvedValue(
        venueCollectiveDataFactory({
          siret: undefined,
        })
      )

      renderCollectiveDataEdition()

      await waitForLoader()

      expect(api.getEducationalPartner).not.toHaveBeenCalled()
    })
  })
})
