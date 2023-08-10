import { screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import {
  CollectiveBookingStatus,
  EducationalInstitutionResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import { DEFAULT_VISIBILITY_FORM_VALUES, Mode } from 'core/OfferEducational'
import * as useNotification from 'hooks/useNotification'
import getOfferRequestInformationsAdapter from 'pages/CollectiveOfferFromRequest/adapters/getOfferRequestInformationsAdapter'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import OldCollectiveOfferVisibility from '..'
import { OldCollectiveOfferVisibilityProps } from '../OldCollectiveOfferVisibility'

vi.mock('apiClient/api', () => ({
  api: {
    getAutocompleteEducationalRedactorsForUai: vi.fn(),
    getCollectiveOfferRequest: vi.fn(),
  },
}))

vi.mock('core/OfferEducational/utils/extractInitialVisibilityValues', () => ({
  __esModule: true,
  extractInitialVisibilityValues: vi.fn(() => ({
    institution: '',
    'search-institution': 'METIER ROBERT DOISNEAU - CORBEIL-ESSONNES',
    teacher: 'compte.test@education.gouv.fr',
    visibility: 'one',
    'search-teacher': 'Reda Khteur',
  })),
}))

const institutions: EducationalInstitutionResponseModel[] = [
  {
    id: 12,
    name: 'Institution 1',
    postalCode: '91190',
    city: 'Gif-sur-Yvette',
    institutionType: 'Collège',
    phoneNumber: '',
    institutionId: 'ABCDEF11',
  },
  {
    id: 24,
    name: 'Institution 2',
    postalCode: '75005',
    city: 'Paris',
    phoneNumber: '',
    institutionId: 'ABCDEF12',
  },
  {
    id: 42,
    name: 'Institution 3',
    postalCode: '33000',
    city: 'Bordeaux',
    phoneNumber: '',
    institutionId: 'ABCDEF13',
  },
  {
    id: 43,
    name: 'METIER ROBERT DOISNEAU',
    postalCode: '91000',
    city: 'CORBEIL-ESSONNES',
    phoneNumber: '',
    institutionId: 'AZERTY13',
  },
]

const renderVisibilityStep = (props: OldCollectiveOfferVisibilityProps) =>
  renderWithProviders(<OldCollectiveOfferVisibility {...props} />)

describe('CollectiveOfferVisibility', () => {
  let props: OldCollectiveOfferVisibilityProps
  const offerId = 1
  beforeEach(() => {
    props = {
      mode: Mode.CREATION,
      patchInstitution: vi.fn(),
      initialValues: DEFAULT_VISIBILITY_FORM_VALUES,
      onSuccess: vi.fn(),
      institutions,
      isLoadingInstitutions: false,
      offer: collectiveOfferFactory({ id: offerId }),
    }
  })

  it('should show banner if generate from publicApi', () => {
    const offer = collectiveOfferFactory({ isPublicApi: true })

    renderVisibilityStep({
      ...props,
      mode: Mode.EDITION,
      offer,
    })
    expect(
      screen.getByText('Offre importée automatiquement')
    ).toBeInTheDocument()
  })

  it('should display booking link for sold out offer with pending booking', () => {
    const offer = collectiveOfferFactory({
      status: OfferStatus.SOLD_OUT,
      lastBookingStatus: CollectiveBookingStatus.PENDING,
      lastBookingId: 76,
    })

    renderVisibilityStep({
      ...props,
      mode: Mode.EDITION,
      offer: offer,
    })

    const bookingLink = screen.getByRole('link', {
      name: 'Voir la préréservation',
    })

    expect(bookingLink).toBeInTheDocument()
  })

  it('should disable visibility form if offer is not editable', async () => {
    props.initialValues = {
      ...props.initialValues,
      institution: '12',
      visibility: 'one',
    }
    renderVisibilityStep({ ...props, mode: Mode.READ_ONLY })
    expect(
      screen.getByLabelText(/Un établissement en particulier/)
    ).toBeDisabled()
    expect(
      await screen.findByPlaceholderText(
        /Saisir l’établissement scolaire ou le code UAI/
      )
    ).toBeDisabled()
    expect(screen.getByText(/Valider et enregistrer l’offre/)).toBeDisabled()
  })

  it('should disable submit button if the user wants his offer to concern one Institution but has selected none', async () => {
    renderVisibilityStep(props)
    await userEvent.click(
      screen.getByLabelText(/Un établissement en particulier/)
    )
    expect(
      screen.getByRole('button', { name: /Étape suivante/ })
    ).toBeDisabled()
  })

  it('should display details on selected institution', async () => {
    const spyPatch = vi.fn().mockResolvedValueOnce({ isOk: true })
    renderVisibilityStep({ ...props, patchInstitution: spyPatch })
    await userEvent.click(
      screen.getByLabelText(/Un établissement en particulier/)
    )

    //  Open the autocomplete select panel
    await userEvent.click(
      await screen.findByPlaceholderText(
        /Saisir l’établissement scolaire ou le code UAI/
      )
    )

    const optionsList = await screen.findByTestId('list')
    expect(optionsList).toBeInTheDocument()

    //  Click an option in the opened panel
    await userEvent.click(
      within(optionsList).getByText(/Collège Institution 1/)
    )

    //  The panel should be closed
    expect(optionsList).not.toBeInTheDocument()

    expect(await screen.findByText(/91190 Gif-sur-Yvette/)).toBeInTheDocument()
  })

  it('should save selected institution and call onSuccess props', async () => {
    const spyPatch = vi
      .fn()
      .mockResolvedValueOnce({ isOk: true, payload: { institutions: [] } })
    renderVisibilityStep({ ...props, patchInstitution: spyPatch })
    await userEvent.click(
      screen.getByLabelText(/Un établissement en particulier/)
    )
    await userEvent.click(
      await screen.findByPlaceholderText(
        /Saisir l’établissement scolaire ou le code UAI/
      )
    )

    const optionsList = await screen.findByTestId('list')
    await userEvent.click(
      within(optionsList).getByText(/Collège Institution 1/)
    )
    await userEvent.click(
      screen.getByRole('button', { name: /Étape suivante/ })
    )
    expect(spyPatch).toHaveBeenCalledTimes(1)
    expect(props.onSuccess).toHaveBeenCalledWith({
      offerId: offerId.toString(),
      message: '',
      payload: {
        institutions: [],
      },
    })
  })

  it('should clear search input field when clicking on the input again', async () => {
    renderVisibilityStep(props)

    const institutionInput = await screen.findByPlaceholderText(
      /Saisir l’établissement scolaire ou le code UAI/
    )
    await userEvent.click(institutionInput)

    await userEvent.type(institutionInput, 'Test input')

    await userEvent.click(await screen.findByTestId(/wrapper-visibility/))

    await userEvent.click(institutionInput)

    expect(institutionInput).toHaveDisplayValue('')
  })

  it('should display an error when the institution could not be saved', async () => {
    const spyPatch = vi
      .fn()
      .mockResolvedValue({ isOk: false, message: 'Ooops' })
    const notifyError = vi.fn()
    // @ts-expect-error
    vi.spyOn(useNotification, 'default').mockImplementation(() => ({
      error: notifyError,
    }))
    renderVisibilityStep({ ...props, patchInstitution: spyPatch })
    await userEvent.click(
      screen.getByLabelText(/Un établissement en particulier/)
    )
    await userEvent.click(
      await screen.findByPlaceholderText(
        /Saisir l’établissement scolaire ou le code UAI/
      )
    )
    const optionsList = await screen.findByTestId('list')
    await userEvent.click(
      within(optionsList).getByText(/Collège Institution 1/)
    )

    await userEvent.click(
      screen.getByRole('button', { name: /Étape suivante/ })
    )
    expect(spyPatch).toHaveBeenCalledTimes(1)
    await waitFor(() => expect(notifyError).toHaveBeenNthCalledWith(1, 'Ooops'))
  })

  it('should display institution type, name and city in select options', async () => {
    renderVisibilityStep(props)
    await userEvent.click(
      screen.getByLabelText(/Un établissement en particulier/)
    )
    await userEvent.click(
      await screen.findByPlaceholderText(
        /Saisir l’établissement scolaire ou le code UAI/
      )
    )
    const optionsList = await screen.findByTestId('list')
    expect(
      await within(optionsList).findByText(
        /Collège Institution 1 - Gif-sur-Yvette/
      )
    ).toBeInTheDocument()
    expect(
      await within(optionsList).findByText(/Institution 2 - Paris/)
    ).toBeInTheDocument()
  })

  it('should trim values when searching in a SelectAutocomplete', async () => {
    renderVisibilityStep(props)
    await userEvent.click(
      screen.getByLabelText(/Un établissement en particulier/)
    )

    const institutionInput = await screen.findByPlaceholderText(
      /Saisir l’établissement scolaire ou le code UAI/
    )
    await userEvent.click(institutionInput)

    await userEvent.type(institutionInput, '   Institu   ')

    const optionsList = await screen.findByTestId('list')

    expect(await within(optionsList).findAllByText(/Institution/)).toHaveLength(
      3
    )
  })

  describe('edition', () => {
    it('shoud prefill form with initial values', async () => {
      renderVisibilityStep({
        ...props,
        mode: Mode.EDITION,
        initialValues: {
          visibility: 'one',
          institution: '12',
          'search-institution': 'Institution 1',
          'search-teacher': 'Teacher 1',
          teacher: 'teacher.teach@example.com',
        },
      })
      expect(
        screen.getByLabelText(/Un établissement en particulier/)
      ).toBeChecked()
      expect(
        await screen.findByText(/91190 Gif-sur-Yvette/)
      ).toBeInTheDocument()
    })
    it('shoud delete institution selection', async () => {
      renderVisibilityStep({
        ...props,
        mode: Mode.EDITION,
        initialValues: {
          visibility: 'one',
          institution: '12',
          'search-institution': 'Institution 1',
          'search-teacher': 'Teacher Teach',
          teacher: 'teacher.teach@example.com',
        },
      })

      expect(
        screen.getByLabelText(/Un établissement en particulier/)
      ).toBeChecked()

      expect(
        await screen.findByText(/91190 Gif-sur-Yvette/)
      ).toBeInTheDocument()

      await userEvent.click(
        screen.getByRole('button', {
          name: /Supprimer/i,
        })
      )
      expect(
        await screen.queryByText(/91190 Gif-sur-Yvette/)
      ).not.toBeInTheDocument()
    })

    it('should hide banner when clicking on trash icon', async () => {
      const spyPatch = vi.fn().mockResolvedValueOnce({
        isOk: true,
        payload: { teacherEmail: 'maria.sklodowska@example.com' },
      })
      renderVisibilityStep({ ...props, patchInstitution: spyPatch })
      await userEvent.click(
        screen.getByLabelText(/Un établissement en particulier/)
      )
      // open hidden select options
      await userEvent.click(
        await screen.findByPlaceholderText(
          /Saisir l’établissement scolaire ou le code UAI/
        )
      )

      const optionsListInstitution = await screen.findByTestId('list')

      //  Click an option in the opened panel
      await userEvent.click(
        within(optionsListInstitution).getByText(/Collège Institution 1/)
      )

      const teacherInput = await screen.findByLabelText(
        /Prénom et nom de l’enseignant/
      )
      // open hidden select options, empty by default
      await userEvent.click(teacherInput)

      vi.spyOn(
        api,
        'getAutocompleteEducationalRedactorsForUai'
      ).mockResolvedValueOnce([
        {
          email: 'maria.sklodowska@example.com',
          gender: 'Mme.',
          name: 'SKLODOWSKA',
          surname: 'MARIA',
        },
      ])
      // filter options to have results
      await userEvent.type(teacherInput, 'mar')

      const optionsListTeacher = await screen.findByTestId('list')

      //  Click an option in the opened panel
      await userEvent.click(
        within(optionsListTeacher).getByText(/MARIA SKLODOWSKA/)
      )

      await userEvent.click(
        screen.getAllByRole('button', {
          name: /Supprimer/i,
        })[1]
      )
      expect(await screen.findAllByText(/MARIA SKLODOWSKA/)).toHaveLength(1)
    })

    it('should prefill form with requested information', async () => {
      vi.spyOn(api, 'getCollectiveOfferRequest').mockResolvedValueOnce({
        comment: 'Test unit',
        redactor: {
          email: 'compte.test@education.gouv.fr',
          firstName: 'Reda',
          lastName: 'Khteur',
        },
        institution: {
          city: 'CORBEIL-ESSONNES',
          institutionId: '123456',
          institutionType: 'LYCEE POLYVALENT',
          name: 'METIER ROBERT DOISNEAU',
          postalCode: '91000',
        },
      })

      vi.spyOn(
        api,
        'getAutocompleteEducationalRedactorsForUai'
      ).mockResolvedValueOnce([
        {
          email: 'compte.test@education.gouv.fr',
          gender: 'Mr.',
          name: 'REDA',
          surname: 'KHTEUR',
        },
      ])

      renderVisibilityStep({
        ...props,
        requestId: '1',
        mode: Mode.CREATION,
        initialValues: DEFAULT_VISIBILITY_FORM_VALUES,
      })

      expect(
        screen.getByLabelText(/Un établissement en particulier/)
      ).toBeChecked()

      expect(
        within(await screen.findByTestId('teacher-banner')).findByText(
          /KHTEUR REDA/
        )
      )

      expect(await screen.findAllByText(/METIER ROBERT DOISNEAU/)).toHaveLength(
        3
      )
      expect(screen.getByText(/91000 CORBEIL-ESSONNES/)).toBeInTheDocument()
      expect(screen.getAllByText(/AZERTY13/)).toHaveLength(3)
    })

    it('should display error message on api error getting requested info', async () => {
      const notifyError = vi.fn()

      vi.spyOn(useNotification, 'default').mockImplementation(() => ({
        ...vi.importActual('hooks/useNotification'),
        error: notifyError,
      }))

      vi.spyOn(api, 'getCollectiveOfferRequest').mockRejectedValue({
        isOk: false,
        message:
          'Une erreur est survenue lors de la récupération de votre offre',
        payload: null,
      })

      renderVisibilityStep({
        ...props,
        requestId: '1',
        mode: Mode.CREATION,
        initialValues: DEFAULT_VISIBILITY_FORM_VALUES,
      })

      const response = await getOfferRequestInformationsAdapter(1)
      expect(response.isOk).toBeFalsy()
      await waitFor(() => {
        expect(notifyError).toHaveBeenCalledTimes(1)
      })
    })
  })
})
