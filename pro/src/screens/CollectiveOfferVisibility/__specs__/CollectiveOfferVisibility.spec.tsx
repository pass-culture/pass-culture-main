import { screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import {
  CollectiveBookingStatus,
  EducationalInstitutionResponseModel,
  OfferStatus,
} from 'apiClient/v1'
import { DEFAULT_VISIBILITY_FORM_VALUES } from 'core/OfferEducational/constants'
import { Mode } from 'core/OfferEducational/types'
import { SENT_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import * as useNotification from 'hooks/useNotification'
import { getCollectiveOfferFactory } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  CollectiveOfferVisibilityScreen,
  CollectiveOfferVisibilityProps,
} from '../CollectiveOfferVisibility'

vi.mock('apiClient/api', () => ({
  api: {
    getAutocompleteEducationalRedactorsForUai: vi.fn(),
    getCollectiveOfferRequest: vi.fn(),
    patchCollectiveOffersEducationalInstitution: vi.fn(),
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

const renderVisibilityStep = (props: CollectiveOfferVisibilityProps) => {
  return renderWithProviders(<CollectiveOfferVisibilityScreen {...props} />)
}

describe('CollectiveOfferVisibility', () => {
  let props: CollectiveOfferVisibilityProps
  const offerId = 1
  beforeEach(() => {
    props = {
      mode: Mode.CREATION,
      initialValues: DEFAULT_VISIBILITY_FORM_VALUES,
      onSuccess: vi.fn(),
      institutions,
      isLoadingInstitutions: false,
      offer: getCollectiveOfferFactory({ id: offerId }),
    }
  })

  it('should show banner if generate from publicApi', () => {
    const offer = getCollectiveOfferFactory({ isPublicApi: true })

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
    const offer = getCollectiveOfferFactory({
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
    }
    renderVisibilityStep({ ...props, mode: Mode.READ_ONLY })
    expect(
      await screen.findByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
      )
    ).toBeDisabled()
    expect(screen.getByText(/Enregistrer les modifications/)).toBeDisabled()
  })

  it('should disable submit button if the user did not select an institution', () => {
    renderVisibilityStep(props)
    expect(
      screen.getByRole('button', { name: /Étape suivante/ })
    ).toBeDisabled()
  })

  it('should display details on selected institution', async () => {
    renderVisibilityStep(props)

    //  Open the autocomplete select panel
    await userEvent.click(
      await screen.findByLabelText(
        /Nom de l’établissement scolaire ou code UAI/
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

    expect(
      await screen.findByText(
        'Collège Institution 1 - Gif-sur-Yvette - ABCDEF11'
      )
    ).toBeInTheDocument()
  })

  it('should save selected institution and call onSuccess props', async () => {
    const resultingOffer = getCollectiveOfferFactory()
    vi.spyOn(
      api,
      'patchCollectiveOffersEducationalInstitution'
    ).mockResolvedValueOnce(resultingOffer)

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
      screen.getByRole('button', { name: /Étape suivante/ })
    )
    expect(
      api.patchCollectiveOffersEducationalInstitution
    ).toHaveBeenCalledTimes(1)
    expect(props.onSuccess).toHaveBeenCalledWith({
      offerId: offerId.toString(),
      message:
        'Les paramètres de visibilité de votre offre ont bien été enregistrés',
      payload: resultingOffer,
    })
  })

  it('should not clear search input field when clicking on the input again', async () => {
    renderVisibilityStep(props)

    const institutionInput = await screen.findByLabelText(
      /Nom de l’établissement scolaire ou code UAI/
    )
    await userEvent.click(institutionInput)

    await userEvent.type(institutionInput, 'Test input')

    await userEvent.click(
      await screen.findByTestId('wrapper-search-institution')
    )

    await userEvent.click(institutionInput)

    expect(institutionInput).toHaveDisplayValue('Test input')
  })

  it('should display an error when the institution could not be saved', async () => {
    vi.spyOn(
      api,
      'patchCollectiveOffersEducationalInstitution'
    ).mockRejectedValueOnce(new Error('Ooops'))
    const notifyError = vi.fn()

    const notifsImport = (await vi.importActual(
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
    }))
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
      screen.getByRole('button', { name: /Étape suivante/ })
    )
    expect(
      api.patchCollectiveOffersEducationalInstitution
    ).toHaveBeenCalledTimes(1)
    await waitFor(() =>
      expect(notifyError).toHaveBeenNthCalledWith(1, SENT_DATA_ERROR_MESSAGE)
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

    const institutionSelect = screen.getAllByTestId('select')[0]
    await userEvent.selectOptions(institutionSelect, '12')
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
    const institutionSelect = screen.getAllByTestId('select')[0]
    await userEvent.selectOptions(institutionSelect, '12')
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
          visibility: 'one',
          institution: '24',
          'search-institution': 'Institution 2',
          'search-teacher': 'Teacher 1',
          teacher: 'teacher.teach@example.com',
        },
      })
      expect(
        await screen.findByText(
          /Option sélectionnée : Institution 2 - Paris - ABCDEF12/
        )
      ).toBeInTheDocument()
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
          institutionId: 'AZERTY13',
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
        mode: Mode.EDITION,
        initialValues: DEFAULT_VISIBILITY_FORM_VALUES,
      })

      expect(
        await screen.findByText(/Option sélectionnée : KHTEUR REDA/)
      ).toBeInTheDocument()
      expect(
        screen.getByText(
          /Option sélectionnée : LYCEE POLYVALENT METIER ROBERT DOISNEAU - CORBEIL-ESSONNES - AZERTY13/
        )
      ).toBeInTheDocument()
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
})
