import 'react-router-dom'

import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { EducationalInstitutionResponseModel } from 'apiClient/v1'
import { DEFAULT_VISIBILITY_FORM_VALUES, Mode } from 'core/OfferEducational'
import * as useNotification from 'hooks/useNotification'
import { collectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveOfferVisibility, {
  CollectiveOfferVisibilityProps,
} from '../CollectiveOfferVisibility'

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    offerId: 'BQ',
  }),
}))

jest.mock('apiClient/api', () => ({
  api: {
    getAutocompleteEducationalRedactorsForUai: jest.fn(),
  },
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
]

const renderVisibilityStep = (props: CollectiveOfferVisibilityProps) =>
  renderWithProviders(<CollectiveOfferVisibility {...props} />)

describe('CollectiveOfferVisibility', () => {
  let props: CollectiveOfferVisibilityProps

  beforeEach(() => {
    props = {
      mode: Mode.CREATION,
      patchInstitution: jest.fn(),
      initialValues: DEFAULT_VISIBILITY_FORM_VALUES,
      onSuccess: jest.fn(),
      institutions,
      isLoadingInstitutions: false,
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
    const spyPatch = jest.fn().mockResolvedValue({ isOk: true })
    renderVisibilityStep({ ...props, patchInstitution: spyPatch })
    await userEvent.click(
      screen.getByLabelText(/Un établissement en particulier/)
    )

    await userEvent.click(
      await screen.findByPlaceholderText(
        /Saisir l’établissement scolaire ou le code UAI/
      )
    )
    await userEvent.click(await screen.findByLabelText(/Collège Institution 1/))
    expect(await screen.findByText(/91190 Gif-sur-Yvette/)).toBeInTheDocument()

    await userEvent.click(
      await screen.findByPlaceholderText(
        /Saisir l’établissement scolaire ou le code UAI/
      )
    )
    await userEvent.click(await screen.findByLabelText(/Institution 2/))
    expect(await screen.findByText(/75005 Paris/)).toBeInTheDocument()
  })

  it('should save selected institution and call onSuccess props', async () => {
    const spyPatch = jest
      .fn()
      .mockResolvedValue({ isOk: true, payload: { institutions: [] } })
    renderVisibilityStep({ ...props, patchInstitution: spyPatch })
    await userEvent.click(
      screen.getByLabelText(/Un établissement en particulier/)
    )
    await userEvent.click(
      await screen.findByPlaceholderText(
        /Saisir l’établissement scolaire ou le code UAI/
      )
    )
    await userEvent.click(await screen.findByLabelText(/Collège Institution 1/))
    await userEvent.click(
      screen.getByRole('button', { name: /Étape suivante/ })
    )
    expect(spyPatch).toHaveBeenCalledTimes(1)
    expect(props.onSuccess).toHaveBeenCalledWith({
      offerId: 'BQ',
      message: '',
      payload: {
        institutions: [],
      },
    })
  })

  it('should display an error when the institution could not be saved', async () => {
    const spyPatch = jest
      .fn()
      .mockResolvedValue({ isOk: false, message: 'Ooops' })
    const notifyError = jest.fn()
    // @ts-expect-error
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
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
    await userEvent.click(await screen.findByLabelText(/Collège Institution 1/))
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
    expect(
      await screen.findByLabelText(/Collège Institution 1 - Gif-sur-Yvette/)
    ).toBeInTheDocument()
    expect(
      await screen.findByLabelText(/Institution 2 - Paris/)
    ).toBeInTheDocument()
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
        await screen.findByText(/Collège Institution 1/)
      ).toBeInTheDocument()
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
        await screen.findByText(/Collège Institution 1/)
      ).toBeInTheDocument()
      expect(
        await screen.findByText(/91190 Gif-sur-Yvette/)
      ).toBeInTheDocument()
      await userEvent.click(
        screen.getByRole('button', {
          name: /Supprimer/i,
        })
      )
      expect(
        await screen.queryByText(/Collège Institution 1/)
      ).not.toBeInTheDocument()
    })

    it('should hide banner when clicking on trash icon', async () => {
      const spyPatch = jest.fn().mockResolvedValue({
        isOk: true,
        payload: { teacherEmail: 'maria.sklodowska@example.com' },
      })
      renderVisibilityStep({ ...props, patchInstitution: spyPatch })
      await userEvent.click(
        screen.getByLabelText(/Un établissement en particulier/)
      )
      await userEvent.click(
        await screen.findByPlaceholderText(
          /Saisir l’établissement scolaire ou le code UAI/
        )
      )
      await userEvent.click(
        await screen.findByLabelText(/Collège Institution 1/)
      )

      const teacherInput = await screen.findByPlaceholderText(
        /Saisir le prénom et le nom de l’enseignant/
      )
      await userEvent.click(teacherInput)

      jest
        .spyOn(api, 'getAutocompleteEducationalRedactorsForUai')
        .mockResolvedValue([
          {
            email: 'maria.sklodowska@example.com',
            gender: 'Mme.',
            name: 'SKLODOWSKA',
            surname: 'MARIA',
          },
        ])
      await userEvent.type(teacherInput, 'mar')
      await userEvent.click(await screen.findByLabelText(/MARIA SKLODOWSKA/))
      await userEvent.click(
        screen.getAllByRole('button', {
          name: /Supprimer/i,
        })[1]
      )
      expect(
        await screen.queryByText(/MARIA SKLODOWSKA/)
      ).not.toBeInTheDocument()
    })
  })
})
