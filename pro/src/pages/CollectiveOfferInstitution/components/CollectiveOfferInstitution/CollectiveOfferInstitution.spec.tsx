import { screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect, it } from 'vitest'

import { apiNew } from '@/apiClient/api'
import {
  CollectiveOfferAllowedAction,
  type EducationalInstitutionResponseModel,
  type EducationalRedactors,
} from '@/apiClient/v1/new'
import { DEFAULT_INSTITUTION_FORM_VALUES } from '@/commons/core/OfferEducational/constants'
import { Mode } from '@/commons/core/OfferEducational/types'
import {
  GET_DATA_ERROR_MESSAGE,
  SENT_DATA_ERROR_MESSAGE,
} from '@/commons/core/shared/constants'
import * as useSnackBar from '@/commons/hooks/useSnackBar'
import {
  defaultGetCollectiveOfferRequest,
  getCollectiveOfferFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  INSTITUTION_GENERIC_ERROR_MESSAGE,
  REDACTOR_GENERIC_ERROR_MESSAGE,
} from '../../commons/constants'
import {
  type CollectiveOfferInstitutionProps,
  CollectiveOfferInstitutionScreen,
} from './CollectiveOfferInstitution'

vi.mock('@/apiClient/api', () => ({
  apiNew: {
    getAutocompleteEducationalRedactorsForUai: vi.fn(),
    getCollectiveOfferRequest: vi.fn(),
    patchCollectiveOffersEducationalInstitution: vi.fn(),
  },
}))

vi.mock('use-debounce', async () => ({
  ...(await vi.importActual('use-debounce')),
  useDebouncedCallback: vi.fn((fn) => fn),
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
    institutionType: 'Collège',
  },
  {
    id: 42,
    name: 'Institution 3',
    postalCode: '33000',
    city: 'Bordeaux',
    phoneNumber: '',
    institutionId: 'ABCDEF13',
    institutionType: 'Collège',
  },
  {
    id: 43,
    name: 'METIER ROBERT DOISNEAU',
    postalCode: '91000',
    city: 'CORBEIL-ESSONNES',
    phoneNumber: '',
    institutionType: 'LYCEE POLYVALENT',
    institutionId: 'AZERTY13',
  },
]

const renderInstitutionStep = (
  props: CollectiveOfferInstitutionProps,
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(<CollectiveOfferInstitutionScreen {...props} />, {
    ...options,
  })
}

describe('CollectiveOfferInstitution', () => {
  let props: CollectiveOfferInstitutionProps
  const offerId = 1
  const offer = getCollectiveOfferFactory({
    id: offerId,
    allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_INSTITUTION],
  })
  const snackBarError = vi.fn()
  const snackBarSuccess = vi.fn()

  beforeEach(async () => {
    const snackBarsImport = (await vi.importActual(
      '@/commons/hooks/useSnackBar'
    )) as ReturnType<typeof useSnackBar.useSnackBar>
    vi.spyOn(useSnackBar, 'useSnackBar').mockImplementation(() => ({
      ...snackBarsImport,
      success: snackBarSuccess,
      error: snackBarError,
    }))

    props = {
      mode: Mode.CREATION,
      initialValues: DEFAULT_INSTITUTION_FORM_VALUES,
      onSuccess: vi.fn(),
      institutions,
      isLoadingInstitutions: false,
      offer,
    }
  })

  it('should show banner if generate from publicApi', () => {
    const offer = getCollectiveOfferFactory({ isPublicApi: true })

    renderInstitutionStep({
      ...props,
      mode: Mode.EDITION,
      offer,
    })

    expect(
      screen.getByText(
        'Cette offre a été importée automatiquement depuis votre système de billetterie.'
      )
    ).toBeInTheDocument()
  })

  it('should disable institution form if institution is not editable', async () => {
    props.initialValues = {
      ...props.initialValues,
      educationalInstitution: '12',
    }
    renderInstitutionStep({ ...props, offer: { ...offer, allowedActions: [] } })
    expect(
      await screen.findByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
      )
    ).toBeDisabled()

    expect(
      screen.getByRole('button', { name: /Enregistrer et continuer/ })
    ).toBeDisabled()
  })

  it('should display details on selected institution', async () => {
    renderInstitutionStep(props)

    const institutionInput = await screen.findByLabelText(
      /Nom de l’établissement scolaire ou code UAI/
    )

    //  Open the autocomplete select panel
    await userEvent.click(institutionInput)

    const optionsList = await screen.findByTestId('list')
    expect(optionsList).toBeInTheDocument()

    //  Click an option in the opened panel
    await userEvent.click(
      within(optionsList).getByText(/Collège Institution 1/)
    )

    //  The panel should be closed
    expect(optionsList).not.toBeInTheDocument()

    expect(institutionInput).toHaveValue(
      'Collège Institution 1 - Gif-sur-Yvette - ABCDEF11'
    )
  })

  it('should submit the form with right data', async () => {
    const resultingOffer = getCollectiveOfferFactory()
    vi.spyOn(
      apiNew,
      'patchCollectiveOffersEducationalInstitution'
    ).mockResolvedValueOnce(resultingOffer)

    vi.spyOn(apiNew, 'getAutocompleteEducationalRedactorsForUai')
      .mockResolvedValueOnce([]) // redactors preloading
      .mockResolvedValueOnce([
        {
          email: 'compte.test@education.gouv.fr',
          name: 'REDA',
          surname: 'KHTEUR',
        },
      ])

    renderInstitutionStep(props)

    const institutionInput = screen.getByLabelText(
      /Nom de l’établissement scolaire ou code UAI/
    )
    await userEvent.type(institutionInput, 'Collège Institution 1')

    await userEvent.keyboard('{ArrowDown}{Enter}')
    expect(
      apiNew.getAutocompleteEducationalRedactorsForUai
    ).toHaveBeenCalledOnce()

    const teacherInput = screen.getByLabelText(/Prénom et nom de l’enseignant/)

    await userEvent.type(teacherInput, 'Red')

    await userEvent.keyboard('{ArrowDown}{Enter}')

    await userEvent.click(
      screen.getByRole('button', { name: /Enregistrer et continuer/ })
    )
    expect(
      apiNew.patchCollectiveOffersEducationalInstitution
    ).toHaveBeenCalledTimes(1)
    expect(
      apiNew.patchCollectiveOffersEducationalInstitution
    ).toHaveBeenCalledWith({
      path: { offer_id: 1 },
      body: {
        educationalInstitutionId: 12,
        teacherEmail: 'compte.test@education.gouv.fr',
      },
    })
    expect(props.onSuccess).toHaveBeenCalledWith({
      offerId: offerId.toString(),
      message:
        'Les paramètres de visibilité de votre offre ont bien été enregistrés',
      payload: resultingOffer,
    })
  })

  it('should display an error when the institution could not be saved', async () => {
    vi.spyOn(
      apiNew,
      'patchCollectiveOffersEducationalInstitution'
    ).mockRejectedValueOnce(new Error('Ooops'))

    renderInstitutionStep(props)

    await userEvent.click(
      await screen.findByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
      )
    )
    const optionsList = await screen.findByTestId('list')
    await userEvent.click(
      within(optionsList).getByText(/Collège Institution 1/)
    )

    await userEvent.click(
      screen.getByRole('button', { name: /Enregistrer et continuer/ })
    )
    expect(
      apiNew.patchCollectiveOffersEducationalInstitution
    ).toHaveBeenCalledTimes(1)
    await waitFor(() =>
      expect(snackBarError).toHaveBeenNthCalledWith(1, SENT_DATA_ERROR_MESSAGE)
    )
  })

  it('should display institution type, name and city in select options', async () => {
    renderInstitutionStep(props)
    await userEvent.click(
      await screen.findByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
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
    renderInstitutionStep(props)

    const institutionInput = await screen.findByLabelText(
      /Nom de l’établissement scolaire ou code UAI/
    )
    await userEvent.click(institutionInput)

    await userEvent.type(institutionInput, '   Institu   ')

    const optionsList = await screen.findByTestId('list')

    expect(await within(optionsList).findAllByText(/Institution/)).toHaveLength(
      3
    )
  })

  it('should clear teacher suggestion when clearing teacher input', async () => {
    renderInstitutionStep(props)

    vi.spyOn(apiNew, 'getAutocompleteEducationalRedactorsForUai')
      .mockResolvedValueOnce([]) // redactors preloading
      .mockResolvedValueOnce([
        {
          email: 'compte.test@education.gouv.fr',
          name: 'REDA',
          surname: 'KHTEUR',
        },
      ])

    const institutionInput = screen.getByLabelText(
      /Nom de l’établissement scolaire ou code UAI/
    )
    await userEvent.type(institutionInput, 'Collège Institution 1')

    await userEvent.keyboard('{ArrowDown}{Enter}')

    const teacherInput = screen.getByLabelText(/Prénom et nom de l’enseignant/)
    await userEvent.type(teacherInput, 'Red')

    expect(
      screen.getByRole('option', { name: 'KHTEUR REDA' })
    ).toBeInTheDocument()

    await userEvent.clear(teacherInput)

    expect(
      screen.queryByRole('option', { name: 'KHTEUR REDA' })
    ).not.toBeInTheDocument()
  })

  it('should clear teacher suggestion when clearing institution', async () => {
    renderInstitutionStep(props)
    vi.spyOn(apiNew, 'getAutocompleteEducationalRedactorsForUai')
      .mockResolvedValueOnce([]) // redactors preloading
      .mockResolvedValueOnce([
        {
          email: 'compte.test@education.gouv.fr',
          name: 'REDA',
          surname: 'KHTEUR',
        },
      ])

    const institutionInput = screen.getByLabelText(
      /Nom de l’établissement scolaire ou code UAI/
    )
    await userEvent.type(institutionInput, 'Collège Institution 1')

    await userEvent.keyboard('{ArrowDown}{Enter}')

    const teacherInput = screen.getByLabelText(/Prénom et nom de l’enseignant/)
    await userEvent.type(teacherInput, 'Red')

    expect(
      screen.getByRole('option', { name: 'KHTEUR REDA' })
    ).toBeInTheDocument()

    await userEvent.type(
      screen.getByLabelText(/Nom de l’établissement scolaire ou code UAI/),
      ' '
    )

    expect(
      screen.queryByRole('option', { name: 'REDA KHTEUR' })
    ).not.toBeInTheDocument()
  })

  describe('edition', () => {
    it('shoud prefill form with initial values', async () => {
      renderInstitutionStep({
        ...props,
        mode: Mode.EDITION,
        initialValues: {
          educationalInstitution: '24',
          teacherEmail: 'teacher.teach@example.com',
        },
      })

      const institutionInput = await screen.findByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
      )

      expect(institutionInput).toHaveValue(
        'Collège Institution 2 - Paris - ABCDEF12'
      )
    })

    it('should prefill form with requested information', async () => {
      const collectiveRequest = {
        ...defaultGetCollectiveOfferRequest,
        comment: 'Test unit',
        redactor: {
          email: 'compte.test@education.gouv.fr',
          firstName: 'Reda',
          lastName: 'Khteur',
        },
        institution: {
          city: 'CORBEIL-ESSONNES',
          institutionId: 'AZERTY13',
          institutionType: 'LYCEE POLYVALENT',
          name: 'METIER ROBERT DOISNEAU',
          postalCode: '91000',
        },
      }
      vi.spyOn(apiNew, 'getCollectiveOfferRequest').mockResolvedValueOnce(
        collectiveRequest
      )

      vi.spyOn(apiNew, 'getAutocompleteEducationalRedactorsForUai')
        .mockResolvedValueOnce([]) // redactors preloading
        .mockResolvedValueOnce([
          {
            email: 'compte.test@education.gouv.fr',
            name: 'REDA',
            surname: 'KHTEUR',
          },
        ])

      renderInstitutionStep({
        ...props,
        requestId: '1',
        mode: Mode.EDITION,
        initialValues: DEFAULT_INSTITUTION_FORM_VALUES,
      })

      const institutionInput = await screen.findByLabelText(
        /Nom de l’établissement scolaire ou code UAI */
      )

      await waitFor(() => {
        expect(institutionInput).toHaveValue(
          'LYCEE POLYVALENT METIER ROBERT DOISNEAU - CORBEIL-ESSONNES - AZERTY13'
        )
      })

      const teacherInput = await screen.findByLabelText(
        /Prénom et nom de l’enseignant/
      )

      await waitFor(() => {
        expect(teacherInput).toHaveValue('Reda Khteur')
      })
    })

    it('should display default institution error message when institution input is not empty but institution is null', async () => {
      vi.spyOn(apiNew, 'patchCollectiveOffersEducationalInstitution')
      renderInstitutionStep({
        ...props,
        mode: Mode.EDITION,
      })

      const institutionInput = await screen.findByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
      )

      await userEvent.type(institutionInput, 'Invalid Institution')

      await userEvent.click(
        screen.getByRole('button', { name: /Enregistrer et continuer/ })
      )
      expect(
        apiNew.patchCollectiveOffersEducationalInstitution
      ).not.toHaveBeenCalled()

      expect(
        await screen.findByText(INSTITUTION_GENERIC_ERROR_MESSAGE)
      ).toBeInTheDocument()
    })

    it('should display teacher generic error message when teacher input is not empty but teacherEmail is null', async () => {
      vi.spyOn(apiNew, 'patchCollectiveOffersEducationalInstitution')
      renderInstitutionStep({
        ...props,
        mode: Mode.EDITION,
        initialValues: {
          educationalInstitution: '24',
        },
      })

      const teacherInput = await screen.findByLabelText(
        /Prénom et nom de l’enseignant/
      )

      await userEvent.type(teacherInput, 'Invalid Teacher')

      await userEvent.click(
        screen.getByRole('button', { name: /Enregistrer et continuer/ })
      )

      expect(
        await screen.findByText(REDACTOR_GENERIC_ERROR_MESSAGE)
      ).toBeInTheDocument()
    })

    it('should display institution specific error message when receiving an api error with form keys', async () => {
      vi.spyOn(
        apiNew,
        'patchCollectiveOffersEducationalInstitution'
      ).mockRejectedValueOnce({
        message: '',
        name: 'ApiError',
        body: {
          educationalInstitution: [INSTITUTION_GENERIC_ERROR_MESSAGE],
        },
      })
      renderInstitutionStep({
        ...props,
        mode: Mode.EDITION,
        initialValues: {
          educationalInstitution: '24',
        },
      })
      await userEvent.click(
        screen.getByRole('button', { name: /Enregistrer et continuer/ })
      )
      expect(
        apiNew.patchCollectiveOffersEducationalInstitution
      ).toHaveBeenCalled()

      expect(screen.getByText(INSTITUTION_GENERIC_ERROR_MESSAGE)).toBeVisible()
    })

    it('should display teacher specific error message when receiving an api error with form keys', async () => {
      vi.spyOn(
        apiNew,
        'patchCollectiveOffersEducationalInstitution'
      ).mockRejectedValueOnce({
        message: '',
        name: 'ApiError',
        body: {
          teacherEmail: [REDACTOR_GENERIC_ERROR_MESSAGE],
        },
      })
      renderInstitutionStep({
        ...props,
        mode: Mode.EDITION,
        initialValues: {
          educationalInstitution: '24',
        },
      })
      await userEvent.click(
        screen.getByRole('button', { name: /Enregistrer et continuer/ })
      )
      expect(
        apiNew.patchCollectiveOffersEducationalInstitution
      ).toHaveBeenCalled()

      expect(screen.getByText(REDACTOR_GENERIC_ERROR_MESSAGE)).toBeVisible()
    })
  })

  it('should have a cancel button instead of the previous step button when editing the offer', () => {
    renderInstitutionStep({ ...props, mode: Mode.EDITION })
    expect(
      screen.queryByRole('button', { name: /Étape suivante/ })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole('button', { name: 'Annuler et quitter' })
    ).not.toBeInTheDocument()
  })

  it('should display saving information in action bar', async () => {
    renderInstitutionStep({ ...props, mode: Mode.CREATION })

    expect(screen.getByText('Brouillon enregistré')).toBeInTheDocument()

    expect(
      await screen.findByRole('button', { name: 'Enregistrer et continuer' })
    ).toBeInTheDocument()
  })

  it('should change saving information in action bar when form value change', async () => {
    renderInstitutionStep({ ...props, mode: Mode.CREATION })

    vi.spyOn(
      apiNew,
      'getAutocompleteEducationalRedactorsForUai'
    ).mockResolvedValueOnce([
      {
        email: 'compte.test@education.gouv.fr',
        name: 'REDA',
        surname: 'KHTEUR',
      },
    ])

    expect(screen.getByText('Brouillon enregistré')).toBeInTheDocument()

    const institutionInput = screen.getByLabelText(
      /Nom de l’établissement scolaire ou code UAI/
    )
    await userEvent.type(institutionInput, 'Collège Institution 1')

    await userEvent.keyboard('{ArrowDown}{Enter}')
    const teacherInput = screen.getByLabelText(/Prénom et nom de l’enseignant/)
    await userEvent.type(teacherInput, 'Red')

    expect(screen.getByText('Brouillon non enregistré')).toBeInTheDocument()

    expect(
      await screen.findByRole('button', { name: 'Enregistrer et continuer' })
    ).toBeInTheDocument()
  })

  it('should not disable institution input when allowedAction CAN_EDIT_INSTITUTION exist', async () => {
    props.initialValues = {
      ...props.initialValues,
      educationalInstitution: '12',
    }
    renderInstitutionStep({
      ...props,
      mode: Mode.READ_ONLY,
    })
    expect(
      await screen.findByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
      )
    ).not.toBeDisabled()
    expect(screen.getByText(/Enregistrer et continuer/)).not.toBeDisabled()
  })

  it('should disable institution input when allowedAction CAN_EDIT_INSTITUTION  doesnt exist', async () => {
    props.initialValues = {
      ...props.initialValues,
      educationalInstitution: '12',
    }
    renderInstitutionStep({
      ...props,
      mode: Mode.READ_ONLY,
      offer: { ...props.offer, allowedActions: [] },
    })
    expect(
      await screen.findByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
      )
    ).toBeDisabled()
    expect(
      screen.getByRole('button', { name: /Enregistrer et continuer/ })
    ).toBeDisabled()
  })

  describe('redactors preloading', () => {
    it('should preload redactors when institution is selected', async () => {
      const resultingOffer = getCollectiveOfferFactory()
      vi.spyOn(
        apiNew,
        'patchCollectiveOffersEducationalInstitution'
      ).mockResolvedValueOnce(resultingOffer)

      let resolvePreload!: (value: EducationalRedactors) => void
      const preloadPromise = new Promise<EducationalRedactors>((resolve) => {
        resolvePreload = resolve
      })
      vi.spyOn(apiNew, 'getAutocompleteEducationalRedactorsForUai')
        .mockImplementationOnce(() => preloadPromise) // redactors preloading
        .mockResolvedValueOnce([
          {
            email: 'compte.test@education.gouv.fr',
            name: 'REDA',
            surname: 'KHTEUR',
          },
        ])

      renderInstitutionStep(props)

      const institutionInput = screen.getByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
      )
      await userEvent.type(institutionInput, 'Collège Institution 1')

      await userEvent.keyboard('{ArrowDown}{Enter}')
      expect(
        apiNew.getAutocompleteEducationalRedactorsForUai
      ).toHaveBeenCalledOnce()

      const teacherInput = screen.getByLabelText(
        /Prénom et nom de l’enseignant/
      )
      expect(teacherInput).toBeDisabled()

      resolvePreload([])

      await waitFor(() => {
        expect(teacherInput).toBeEnabled()
      })
    })

    it('should handle 404 Not Found error when fetching redactors', async () => {
      vi.spyOn(
        apiNew,
        'getAutocompleteEducationalRedactorsForUai'
      ).mockRejectedValueOnce({
        status: 404,
        message: 'not found',
        name: 'ApiError',
      })
      vi.spyOn(console, 'warn').mockImplementation(vi.fn())

      renderInstitutionStep(props)

      const institutionInput = screen.getByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
      )
      await userEvent.type(institutionInput, 'Collège Institution 1')

      await userEvent.keyboard('{ArrowDown}{Enter}')
      expect(
        apiNew.getAutocompleteEducationalRedactorsForUai
      ).toHaveBeenCalledOnce()

      const teacherInput = screen.getByLabelText(
        /Prénom et nom de l’enseignant/
      )

      expect(console.warn).toHaveBeenLastCalledWith('No redactors found')

      await waitFor(() => {
        expect(teacherInput).toBeEnabled()
      })
    })

    it('should display an error if redactors fetching fails', async () => {
      vi.spyOn(
        apiNew,
        'getAutocompleteEducationalRedactorsForUai'
      ).mockRejectedValueOnce(new Error('Ooops'))

      renderInstitutionStep(props)

      const institutionInput = screen.getByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
      )
      await userEvent.type(institutionInput, 'Collège Institution 1')

      await userEvent.keyboard('{ArrowDown}{Enter}')
      expect(
        apiNew.getAutocompleteEducationalRedactorsForUai
      ).toHaveBeenCalledOnce()

      const teacherInput = screen.getByLabelText(
        /Prénom et nom de l’enseignant/
      )

      await waitFor(() =>
        expect(snackBarError).toHaveBeenNthCalledWith(1, GET_DATA_ERROR_MESSAGE)
      )

      await waitFor(() => {
        expect(teacherInput).toBeEnabled()
      })
    })
  })
})
