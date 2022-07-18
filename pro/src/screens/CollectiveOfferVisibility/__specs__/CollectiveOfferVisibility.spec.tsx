import '@testing-library/jest-dom'
import 'react-router-dom'

import * as useNotification from 'components/hooks/useNotification'

import CollectiveOfferVisibility, {
  CollectiveOfferVisibilityProps,
} from '../CollectiveOfferVisibility'
import { DEFAULT_VISIBILITY_FORM_VALUES, Mode } from 'core/OfferEducational'
import { render, screen, waitFor } from '@testing-library/react'

import { EducationalInstitutionResponseModel } from 'apiClient/v1'
import { MemoryRouter } from 'react-router'
import { Provider } from 'react-redux'
import React from 'react'
import { configureTestStore } from 'store/testUtils'
import userEvent from '@testing-library/user-event'

const mockHistoryPush = jest.fn()

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useParams: () => ({
    offerId: 'BQ',
  }),
  useHistory: () => ({
    push: mockHistoryPush,
  }),
}))

const institutions: EducationalInstitutionResponseModel[] = [
  {
    id: 12,
    name: 'Institution 1',
    postalCode: '91190',
    city: 'Gif-sur-Yvette',
  },
  {
    id: 24,
    name: 'Institution 2',
    postalCode: '75005',
    city: 'Paris',
  },
  {
    id: 42,
    name: 'Institution 3',
    postalCode: '33000',
    city: 'Bordeaux',
  },
]

export const renderVisibilityStep = (props: CollectiveOfferVisibilityProps) => {
  render(
    <Provider store={configureTestStore()}>
      <MemoryRouter>
        <CollectiveOfferVisibility {...props} />
      </MemoryRouter>
    </Provider>
  )
}

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

  it('should disable visibility form if offer is not editable', async () => {
    renderVisibilityStep({ ...props, mode: Mode.READ_ONLY })
    expect(
      screen.getByLabelText(/Un établissement en particulier/)
    ).toBeDisabled()
    expect(screen.getByText(/Valider et enregistrer l’offre/)).toBeDisabled()
  })

  it('should disable submit button if the user wants his offer to concern one Institution but has selected none', async () => {
    renderVisibilityStep(props)
    await userEvent.click(
      screen.getByLabelText(/Un établissement en particulier/)
    )
    expect(
      screen.getByRole('button', { name: /Valider et créer l’offre/ })
    ).toBeDisabled()
  })

  it('should display details on selected institution', async () => {
    const spyPatch = jest.fn().mockResolvedValue({ isOk: true })
    renderVisibilityStep({ ...props, patchInstitution: spyPatch })
    await userEvent.click(
      screen.getByLabelText(/Un établissement en particulier/)
    )
    await userEvent.click(
      await screen.findByPlaceholderText(/Saisir l’établissement scolaire/)
    )
    await userEvent.click(await screen.findByLabelText(/Institution 1/))
    expect(await screen.findByText(/91190 Gif-sur-Yvette/)).toBeInTheDocument()
  })

  it('should save selected institution and call onSuccess props', async () => {
    const spyPatch = jest.fn().mockResolvedValue({ isOk: true })
    renderVisibilityStep({ ...props, patchInstitution: spyPatch })
    await userEvent.click(
      screen.getByLabelText(/Un établissement en particulier/)
    )
    await userEvent.click(
      await screen.findByPlaceholderText(/Saisir l’établissement scolaire/)
    )
    await userEvent.click(await screen.findByLabelText(/Institution 1/))
    await userEvent.click(
      screen.getByRole('button', { name: /Valider et créer l’offre/ })
    )
    expect(spyPatch).toHaveBeenCalledTimes(1)
    expect(props.onSuccess).toHaveBeenCalledWith({ offerId: 'BQ', message: '' })
  })

  it('should display an error when the institution could not be saved', async () => {
    const spyPatch = jest
      .fn()
      .mockResolvedValue({ isOk: false, message: 'Ooops' })
    const notifyError = jest.fn()
    // @ts-ignore
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      error: notifyError,
    }))
    renderVisibilityStep({ ...props, patchInstitution: spyPatch })
    await userEvent.click(
      screen.getByLabelText(/Un établissement en particulier/)
    )
    await userEvent.click(
      await screen.findByPlaceholderText(/Saisir l’établissement scolaire/)
    )
    await userEvent.click(await screen.findByLabelText(/Institution 1/))
    await userEvent.click(
      screen.getByRole('button', { name: /Valider et créer l’offre/ })
    )
    expect(spyPatch).toHaveBeenCalledTimes(1)
    await waitFor(() => expect(notifyError).toHaveBeenNthCalledWith(1, 'Ooops'))
  })

  it('should display institution name and city in select options', async () => {
    renderVisibilityStep(props)
    await userEvent.click(
      screen.getByLabelText(/Un établissement en particulier/)
    )
    await userEvent.click(
      await screen.findByPlaceholderText(/Saisir l’établissement scolaire/)
    )
    expect(
      await screen.findByLabelText(/Institution 1 - Gif-sur-Yvette/)
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
        },
      })
      expect(
        screen.getByLabelText(/Un établissement en particulier/)
      ).toBeChecked()
      expect(await screen.findByText(/Institution 1/)).toBeInTheDocument()
      expect(
        await screen.findByText(/91190 Gif-sur-Yvette/)
      ).toBeInTheDocument()
    })

    it('should disable form if user has not made any modifications', async () => {
      renderVisibilityStep({
        ...props,
        mode: Mode.EDITION,
        initialValues: {
          visibility: 'one',
          institution: '12',
          'search-institution': 'Institution 1',
        },
      })
      expect(
        screen.getByRole('button', { name: /Valider et enregistrer l’offre/ })
      ).toBeDisabled()
    })
  })
})
