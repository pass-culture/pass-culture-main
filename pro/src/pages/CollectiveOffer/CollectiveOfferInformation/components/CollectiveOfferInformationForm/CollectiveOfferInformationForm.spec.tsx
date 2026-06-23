import { screen } from '@testing-library/dom'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { ApiError } from '@/apiClient/compat'
import { CollectiveOfferAllowedAction } from '@/apiClient/v1'
import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  CollectiveOfferInformationForm,
  type CollectiveOfferInformationFormProps,
} from './CollectiveOfferInformationForm'

function renderCollectiveOfferInformationForm(
  props: Partial<CollectiveOfferInformationFormProps>
) {
  const allProps = {
    offer: getCollectiveOfferFactory(),
    isCreation: true,
    saveAndContinue: vi.fn(),
    goBackLink: '/test/go/back/link',
    ...props,
  }
  return renderWithProviders(<CollectiveOfferInformationForm {...allProps} />)
}

describe('<CollectiveOfferInformationForm />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderCollectiveOfferInformationForm({})

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display all form fields for "information pratiques" step', () => {
    renderCollectiveOfferInformationForm({})
    expect(
      screen.getByText(/Les champs suivis d’un \* sont obligatoires/)
    ).toBeVisible()
    expect(screen.getByLabelText(/téléphone/)).toBeVisible()
    expect(screen.getByLabelText('Email*')).toBeVisible()
    expect(
      screen.getByLabelText('Email auquel envoyer les notifications*')
    ).toBeVisible()
    expect(
      screen.getByRole('textbox', {
        name: 'Informations pratiques sur votre offre',
      })
    ).toBeVisible()
  })

  it('should add notification mail input when button is clicked', async () => {
    const user = userEvent.setup()
    const offer = getCollectiveOfferFactory({
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DETAILS],
      bookingEmails: ['test@example.com'],
    })
    renderCollectiveOfferInformationForm({ offer })

    expect(
      screen.getAllByLabelText('Email auquel envoyer les notifications*')
    ).toHaveLength(1)

    const addEmailBtn = screen.getByRole('button', {
      name: 'Ajouter un email de notification',
    })
    await user.click(addEmailBtn)
    await user.click(addEmailBtn)

    expect(
      screen.getAllByLabelText('Email auquel envoyer les notifications*')
    ).toHaveLength(3)
  })

  it('should remove notification mail input when trash icon is clicked', async () => {
    const user = userEvent.setup()
    const offer = getCollectiveOfferFactory({
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DETAILS],
      bookingEmails: ['test1@example.com', 'test2@example.com'],
    })
    renderCollectiveOfferInformationForm({ offer })

    expect(
      screen.getAllByLabelText('Email auquel envoyer les notifications*')
    ).toHaveLength(2)
    const removeInputIcon = screen.getByRole('button', {
      name: 'Supprimer l’email',
    })
    await user.click(removeInputIcon)
    expect(
      screen.getAllByLabelText('Email auquel envoyer les notifications*')
    ).toHaveLength(1)
  })

  it('should disable submition when CAN_EDIT_DETAILS is not among the allowed actions', () => {
    const offer = getCollectiveOfferFactory({
      allowedActions: [CollectiveOfferAllowedAction.CAN_ARCHIVE],
    })
    renderCollectiveOfferInformationForm({ offer })
    expect(screen.getByRole('button', { name: /Enregistrer/ })).toBeDisabled()
  })

  it('should call saveAndContinue prop on form submit, with dirty fields', async () => {
    const user = userEvent.setup()
    const offer = getCollectiveOfferFactory({
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DETAILS],
      bookingEmails: ['test1@example.com'],
      contactEmail: 'contact@example.com',
    })
    const saveAndContinue = vi.fn()
    renderCollectiveOfferInformationForm({ offer, saveAndContinue })

    expect(
      screen.getByRole('button', { name: /Enregistrer/ })
    ).not.toBeDisabled()

    const addEmailBtn = screen.getByRole('button', {
      name: 'Ajouter un email de notification',
    })
    await user.click(addEmailBtn)
    const newBookingEmail = screen.getAllByLabelText(
      'Email auquel envoyer les notifications*'
    )[1]
    await user.type(newBookingEmail, 'test2@example.com')
    await user.clear(screen.getByLabelText(/téléphone/))
    await user.type(screen.getByLabelText(/téléphone/), '6 12 34 56 78')
    await user.type(
      screen.getByRole('textbox', {
        name: 'Informations pratiques sur votre offre',
      }),
      'Test additional details'
    )
    // Touch the email field but don't make it dirty
    await user.clear(screen.getByLabelText('Email*'))
    await user.type(screen.getByLabelText('Email*'), 'contact@example.com')

    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))

    expect(saveAndContinue).toHaveBeenCalledExactlyOnceWith({
      additionalDetails: 'Test additional details',
      bookingEmails: ['test1@example.com', 'test2@example.com'],
      contactPhone: '+33612345678',
    })
  })

  it('should display field errors on API error with status 400', async () => {
    const user = userEvent.setup()
    const error = new ApiError('', 400, 'Bad Request', {
      additionalDetails: ['Erreur sur ce champ !'],
      'bookingEmails.0.email': ['Erreur sur ce booking email'],
    })
    const offer = getCollectiveOfferFactory({
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DETAILS],
    })
    const saveAndContinue = vi.fn().mockRejectedValueOnce(error)
    renderCollectiveOfferInformationForm({ offer, saveAndContinue })

    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))
    expect(screen.getByText('Erreur sur ce champ !')).toBeVisible()
    expect(screen.getByText('Erreur sur ce booking email')).toBeVisible()
  })
})
