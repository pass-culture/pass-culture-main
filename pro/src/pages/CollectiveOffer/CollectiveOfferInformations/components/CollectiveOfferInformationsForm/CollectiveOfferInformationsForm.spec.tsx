import { screen } from '@testing-library/dom'
import userEvent from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { ApiError } from '@/apiClient/compat'
import { CollectiveOfferAllowedAction } from '@/apiClient/v1/new'
import { getCollectiveOfferFactory } from '@/commons/utils/factories/collectiveApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  CollectiveOfferInformationsForm,
  type CollectiveOfferInformationsFormProps,
} from './CollectiveOfferInformationsForm'

vi.mock(
  '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/OfferEducationalForm/FormContact/FormContactNew',
  () => ({
    FormContactNew: vi.fn(() => <div data-testid="contact-form" />),
  })
)

vi.mock(
  '@/pages/CollectiveOffer/CollectiveOffer/components/OfferEducational/OfferEducationalForm/FormNotifications/FormNotifications',
  () => ({
    FormNotifications: vi.fn(() => <div data-testid="notifications-form" />),
  })
)

function renderCollectiveOfferInformationForm(
  props: Partial<CollectiveOfferInformationsFormProps>
) {
  const allProps = {
    offer: getCollectiveOfferFactory(),
    isCreation: true,
    saveAndContinue: vi.fn(),
    goBackLink: '/test/go/back/link',
    ...props,
  }
  return renderWithProviders(<CollectiveOfferInformationsForm {...allProps} />)
}

describe('<CollectiveOfferInformationsForm />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderCollectiveOfferInformationForm({})

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display all form fields for "information pratiques" step', () => {
    renderCollectiveOfferInformationForm({})
    expect(
      screen.getByText(/Les champs suivis d’un \* sont obligatoires/)
    ).toBeVisible()
    expect(screen.getByTestId('contact-form')).toBeVisible()
    expect(screen.getByTestId('notifications-form')).toBeVisible()
    expect(
      screen.getByRole('textbox', {
        name: 'Informations pratiques sur votre offre',
      })
    ).toBeVisible()
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
    })
    const saveAndContinue = vi.fn()
    renderCollectiveOfferInformationForm({ offer, saveAndContinue })

    expect(
      screen.getByRole('button', { name: /Enregistrer/ })
    ).not.toBeDisabled()

    await user.type(
      screen.getByRole('textbox', {
        name: 'Informations pratiques sur votre offre',
      }),
      'Test additional details'
    )
    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))

    expect(saveAndContinue).toHaveBeenCalledExactlyOnceWith({
      additionalDetails: 'Test additional details',
    })
  })

  it('should display field errors on API error with status 400', async () => {
    const user = userEvent.setup()
    const error = new ApiError('', 400, 'Bad Request', {
      additionalDetails: ['Erreur sur ce champ !'],
    })
    const offer = getCollectiveOfferFactory({
      allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DETAILS],
    })
    const saveAndContinue = vi.fn().mockRejectedValueOnce(error)
    renderCollectiveOfferInformationForm({ offer, saveAndContinue })

    await user.click(screen.getByRole('button', { name: /Enregistrer/ }))
    expect(screen.getByText('Erreur sur ce champ !')).toBeVisible()
  })
})
