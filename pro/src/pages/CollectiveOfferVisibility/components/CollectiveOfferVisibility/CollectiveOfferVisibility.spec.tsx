import { act, screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { expect, it } from 'vitest'

import type { ApiRequestOptions } from '@/apiClient/adage/core/ApiRequestOptions'
import type { ApiResult } from '@/apiClient/adage/core/ApiResult'
import { api } from '@/apiClient/api'
import {
  ApiError,
  CancelablePromise,
  CollectiveOfferAllowedAction,
  type EducationalInstitutionResponseModel,
  type EducationalRedactors,
} from '@/apiClient/v1'
import { DEFAULT_VISIBILITY_FORM_VALUES } from '@/commons/core/OfferEducational/constants'
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
  POST_VISIBILITY_FORM_ERROR_MESSAGE,
  REDACTOR_GENERIC_ERROR_MESSAGE,
} from '../../commons/constants'
import {
  type CollectiveOfferVisibilityProps,
  CollectiveOfferVisibilityScreen,
} from './CollectiveOfferVisibility'

vi.mock('@/apiClient/api', () => ({
  api: {
    getAutocompleteEducationalRedactorsForUai: vi.fn(),
    getCollectiveOfferRequest: vi.fn(),
    patchCollectiveOffersEducationalInstitution: vi.fn(),
  },
}))

class Deferred<T> {
  promise: CancelablePromise<T>
  resolve!: (value: T | PromiseLike<T>) => void
  reject!: ({
    status,
    message,
    name,
  }: {
    status: number
    message: string
    name: string
  }) => void

  constructor() {
    this.promise = new CancelablePromise<T>((resolve, reject) => {
      this.resolve = resolve
      this.reject = reject
    })
  }
}

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
    institutionType: 'LYCEE POLYVALENT',
    institutionId: 'AZERTY13',
  },
]

const renderVisibilityStep = (
  props: CollectiveOfferVisibilityProps,
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(<CollectiveOfferVisibilityScreen {...props} />, {
    ...options,
  })
}

describe('CollectiveOfferVisibility', () => {
  let props: CollectiveOfferVisibilityProps
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
      initialValues: DEFAULT_VISIBILITY_FORM_VALUES,
      onSuccess: vi.fn(),
      institutions,
      isLoadingInstitutions: false,
      offer,
    }
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  it('should show banner if generate from publicApi', () => {
    const offer = getCollectiveOfferFactory({ isPublicApi: true })

    renderVisibilityStep({
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

  it('should disable visibility form if institution is not editable', async () => {
    props.initialValues = {
      ...props.initialValues,
      institution: '12',
    }
    renderVisibilityStep({ ...props, offer: { ...offer, allowedActions: [] } })
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
    renderVisibilityStep(props)

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
      api,
      'patchCollectiveOffersEducationalInstitution'
    ).mockResolvedValueOnce(resultingOffer)

    vi.spyOn(api, 'getAutocompleteEducationalRedactorsForUai')
      .mockResolvedValueOnce([]) // redactors preloading
      .mockResolvedValueOnce([
        {
          email: 'compte.test@education.gouv.fr',
          gender: 'Mr.',
          name: 'REDA',
          surname: 'KHTEUR',
        },
      ])

    renderVisibilityStep(props)

    const institutionInput = screen.getByLabelText(
      /Nom de l’établissement scolaire ou code UAI/
    )
    await userEvent.type(institutionInput, 'Collège Institution 1')

    await userEvent.keyboard('{ArrowDown}{Enter}')
    expect(api.getAutocompleteEducationalRedactorsForUai).toHaveBeenCalledOnce()

    const teacherInput = screen.getByLabelText(/Prénom et nom de l’enseignant/)

    await userEvent.type(teacherInput, 'Red')

    await userEvent.keyboard('{ArrowDown}{Enter}')

    await userEvent.click(
      screen.getByRole('button', { name: /Enregistrer et continuer/ })
    )
    expect(
      api.patchCollectiveOffersEducationalInstitution
    ).toHaveBeenCalledTimes(1)
    expect(
      api.patchCollectiveOffersEducationalInstitution
    ).toHaveBeenCalledWith(1, {
      educationalInstitutionId: 12,
      teacherEmail: 'compte.test@education.gouv.fr',
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
      api,
      'patchCollectiveOffersEducationalInstitution'
    ).mockRejectedValueOnce(new Error('Ooops'))

    renderVisibilityStep(props)

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
      api.patchCollectiveOffersEducationalInstitution
    ).toHaveBeenCalledTimes(1)
    await waitFor(() =>
      expect(snackBarError).toHaveBeenNthCalledWith(1, SENT_DATA_ERROR_MESSAGE)
    )
  })

  it('should display institution type, name and city in select options', async () => {
    renderVisibilityStep(props)
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
    renderVisibilityStep(props)

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
    renderVisibilityStep(props)

    vi.spyOn(api, 'getAutocompleteEducationalRedactorsForUai')
      .mockResolvedValueOnce([]) // redactors preloading
      .mockResolvedValueOnce([
        {
          email: 'compte.test@education.gouv.fr',
          gender: 'Mr.',
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
    renderVisibilityStep(props)
    vi.spyOn(api, 'getAutocompleteEducationalRedactorsForUai')
      .mockResolvedValueOnce([]) // redactors preloading
      .mockResolvedValueOnce([
        {
          email: 'compte.test@education.gouv.fr',
          gender: 'Mr.',
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
      screen.queryByRole('option', { name: 'KHTEUR REDA' })
    ).not.toBeInTheDocument()
  })

  describe('edition', () => {
    it('shoud prefill form with initial values', async () => {
      renderVisibilityStep({
        ...props,
        mode: Mode.EDITION,
        initialValues: {
          institution: '24',
          teacher: 'teacher.teach@example.com',
        },
      })

      const institutionInput = await screen.findByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
      )

      expect(institutionInput).toHaveValue('Institution 2 - Paris - ABCDEF12')
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
      vi.spyOn(api, 'getCollectiveOfferRequest').mockResolvedValueOnce(
        collectiveRequest
      )

      vi.spyOn(api, 'getAutocompleteEducationalRedactorsForUai')
        .mockResolvedValueOnce([]) // redactors preloading
        .mockResolvedValueOnce([
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
        mode: Mode.EDITION,
        initialValues: DEFAULT_VISIBILITY_FORM_VALUES,
      })

      const institutionInput = await screen.findByLabelText(
        /Nom de l’établissement scolaire ou code UAI */
      )

      expect(institutionInput).toHaveValue(
        'LYCEE POLYVALENT METIER ROBERT DOISNEAU - CORBEIL-ESSONNES - AZERTY13'
      )

      const teacherInput = await screen.findByLabelText(
        /Prénom et nom de l’enseignant/
      )

      expect(teacherInput).toHaveValue('Khteur Reda')
    })

    it('should display default institution error message when institution input is not empty but institution is null', async () => {
      vi.spyOn(api, 'patchCollectiveOffersEducationalInstitution')
      renderVisibilityStep({
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
        api.patchCollectiveOffersEducationalInstitution
      ).not.toHaveBeenCalled()

      expect(
        await screen.findByText(INSTITUTION_GENERIC_ERROR_MESSAGE)
      ).toBeInTheDocument()
    })

    it('should display teacher generic error message when teacher input is not empty but teacherEmail is null', async () => {
      vi.spyOn(api, 'patchCollectiveOffersEducationalInstitution')
      renderVisibilityStep({
        ...props,
        mode: Mode.EDITION,
        initialValues: {
          institution: '24',
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
        api.patchCollectiveOffersEducationalInstitution
      ).not.toHaveBeenCalled()

      expect(
        await screen.findByText(REDACTOR_GENERIC_ERROR_MESSAGE)
      ).toBeInTheDocument()
    })

    it('should display institution generic error message when receiving an api error with form keys', async () => {
      vi.spyOn(
        api,
        'patchCollectiveOffersEducationalInstitution'
      ).mockRejectedValueOnce(
        new ApiError(
          {} as ApiRequestOptions,
          {
            status: 400,
            body: {
              educationalInstitutionId: ['Erreur api surcharge cote front'],
            },
          } as ApiResult,
          ''
        )
      )
      renderVisibilityStep({
        ...props,
        mode: Mode.EDITION,
        initialValues: {
          institution: '24',
        },
      })
      await userEvent.click(
        screen.getByRole('button', { name: /Enregistrer et continuer/ })
      )
      expect(api.patchCollectiveOffersEducationalInstitution).toHaveBeenCalled()

      expect(
        screen.queryByText(INSTITUTION_GENERIC_ERROR_MESSAGE)
      ).toBeInTheDocument()

      await waitFor(() =>
        expect(snackBarError).toHaveBeenNthCalledWith(
          1,
          POST_VISIBILITY_FORM_ERROR_MESSAGE
        )
      )
    })

    it('should display teacher generic error message when receiving an api error with form keys', async () => {
      vi.spyOn(
        api,
        'patchCollectiveOffersEducationalInstitution'
      ).mockRejectedValueOnce(
        new ApiError(
          {} as ApiRequestOptions,
          {
            status: 400,
            body: {
              teacherEmail: ['Erreur api surcharge cote front'],
            },
          } as ApiResult,
          ''
        )
      )
      renderVisibilityStep({
        ...props,
        mode: Mode.EDITION,
        initialValues: {
          institution: '24',
        },
      })
      await userEvent.click(
        screen.getByRole('button', { name: /Enregistrer et continuer/ })
      )
      expect(api.patchCollectiveOffersEducationalInstitution).toHaveBeenCalled()

      expect(
        screen.queryByText(REDACTOR_GENERIC_ERROR_MESSAGE)
      ).toBeInTheDocument()

      await waitFor(() =>
        expect(snackBarError).toHaveBeenNthCalledWith(
          1,
          POST_VISIBILITY_FORM_ERROR_MESSAGE
        )
      )
    })
  })

  it('should have a cancel button instead of the previous step button when editing the offer', () => {
    renderVisibilityStep({ ...props, mode: Mode.EDITION })
    expect(
      screen.queryByRole('button', { name: /Étape suivante/ })
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole('button', { name: 'Annuler et quitter' })
    ).not.toBeInTheDocument()
  })

  it('should display saving information in action bar', async () => {
    renderVisibilityStep({ ...props, mode: Mode.CREATION })

    expect(screen.getByText('Brouillon enregistré')).toBeInTheDocument()

    expect(
      await screen.findByRole('button', { name: 'Enregistrer et continuer' })
    ).toBeInTheDocument()
  })

  it('should change saving information in action bar when form value change', async () => {
    renderVisibilityStep({ ...props, mode: Mode.CREATION })

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
      institution: '12',
    }
    renderVisibilityStep({
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
      institution: '12',
    }
    renderVisibilityStep({
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
        api,
        'patchCollectiveOffersEducationalInstitution'
      ).mockResolvedValueOnce(resultingOffer)

      const deferred = new Deferred<EducationalRedactors>()
      vi.spyOn(api, 'getAutocompleteEducationalRedactorsForUai')
        .mockImplementationOnce(
          (_uai: string, _candidate: string) => deferred.promise
        ) // redactors preloading
        .mockResolvedValueOnce([
          {
            email: 'compte.test@education.gouv.fr',
            gender: 'Mr.',
            name: 'REDA',
            surname: 'KHTEUR',
          },
        ])

      renderVisibilityStep(props)

      const institutionInput = screen.getByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
      )
      await userEvent.type(institutionInput, 'Collège Institution 1')

      await userEvent.keyboard('{ArrowDown}{Enter}')
      expect(
        api.getAutocompleteEducationalRedactorsForUai
      ).toHaveBeenCalledOnce()

      const teacherInput = screen.getByLabelText(
        /Prénom et nom de l’enseignant/
      )
      expect(teacherInput).toBeDisabled()

      await act(async () => await deferred.resolve([]))

      await waitFor(() => {
        expect(teacherInput).toBeEnabled()
      })
    })

    it('should handle 404 Not Found error when fetching redactors', async () => {
      vi.spyOn(
        api,
        'getAutocompleteEducationalRedactorsForUai'
      ).mockRejectedValueOnce({
        status: 404,
        message: 'not found',
        name: 'ApiError',
      })
      vi.spyOn(console, 'warn').mockImplementation(vi.fn())

      renderVisibilityStep(props)

      const institutionInput = screen.getByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
      )
      await userEvent.type(institutionInput, 'Collège Institution 1')

      await userEvent.keyboard('{ArrowDown}{Enter}')
      expect(
        api.getAutocompleteEducationalRedactorsForUai
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
        api,
        'getAutocompleteEducationalRedactorsForUai'
      ).mockRejectedValueOnce(new Error('Ooops'))

      renderVisibilityStep(props)

      const institutionInput = screen.getByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
      )
      await userEvent.type(institutionInput, 'Collège Institution 1')

      await userEvent.keyboard('{ArrowDown}{Enter}')
      expect(
        api.getAutocompleteEducationalRedactorsForUai
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
