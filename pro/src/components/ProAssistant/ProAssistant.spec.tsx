import { screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import type { PostProAssistantMessageResponseModel } from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { ProAssistantEvents } from '@/commons/core/FirebaseEvents/constants'
import { makeApiError } from '@/commons/utils/factories/errorFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ProAssistant } from './ProAssistant'

const answer: PostProAssistantMessageResponseModel = {
  conversationId: 'a'.repeat(32),
  answer: 'Rendez-vous sur la page **Guichet** pour valider la contremarque.',
  links: [{ label: 'Guichet', path: '/guichet' }],
  helpArticles: [
    {
      title: 'Comment valider une contremarque ?',
      url: 'https://aide.passculture.app/hc/fr/articles/42',
    },
  ],
  outOfScope: false,
}

const renderProAssistant = ({
  features = ['WIP_ENABLE_PRO_ASSISTANT'],
  path = '/accueil',
  isLoggedIn = true,
}: {
  features?: string[]
  path?: string
  isLoggedIn?: boolean
} = {}) =>
  renderWithProviders(<ProAssistant />, {
    features,
    user: isLoggedIn ? sharedCurrentUserFactory() : null,
    initialRouterEntries: [path],
    storeOverrides: {
      user: {
        selectedPartnerVenue: makeGetVenueResponseModel({
          id: 7,
          managingOfferer: {
            id: 12,
            isClosed: false,
            isValidated: true,
            name: 'Entité 12',
            siren: '123456789',
          },
        }),
      },
    },
  })

describe('ProAssistant', () => {
  const mockLogEvent = vi.fn()

  beforeEach(() => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
    vi.spyOn(api, 'postProAssistantMessage').mockResolvedValue(answer)
  })

  it('should not render when the feature is disabled', () => {
    renderProAssistant({ features: [] })

    expect(
      screen.queryByRole('button', { name: 'Demander à Culturo' })
    ).not.toBeInTheDocument()
  })

  it('should not render when the user is not logged in', () => {
    renderProAssistant({ isLoggedIn: false })

    expect(
      screen.queryByRole('button', { name: 'Demander à Culturo' })
    ).not.toBeInTheDocument()
  })

  it('should not render in the ADAGE iframe', () => {
    renderProAssistant({ path: '/adage-iframe/recherche' })

    expect(
      screen.queryByRole('button', { name: 'Demander à Culturo' })
    ).not.toBeInTheDocument()
  })

  it('should open the panel with suggestions and a privacy notice', async () => {
    const { container } = renderProAssistant()

    await userEvent.click(
      screen.getByRole('button', { name: 'Demander à Culturo' })
    )

    expect(screen.getByRole('heading', { name: 'Culturo' })).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Fermer Culturo', expanded: true })
    ).toBeInTheDocument()
    expect(screen.getByText(/je suis/)).toHaveTextContent(
      'Bonjour, je suis Culturo !'
    )
    expect(
      screen.getByText(/Ne saisissez pas de données personnelles/)
    ).toBeInTheDocument()
    expect(
      within(
        screen.getByRole('list', { name: 'Exemples de questions' })
      ).getByRole('button', { name: 'Comment valider une contremarque ?' })
    ).toBeInTheDocument()
    expect(mockLogEvent).toHaveBeenCalledWith(
      ProAssistantEvents.OPENED_PRO_ASSISTANT
    )
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should send a question and display the answer with links', async () => {
    renderProAssistant({ path: '/offres' })
    await userEvent.click(
      screen.getByRole('button', { name: 'Demander à Culturo' })
    )

    await userEvent.type(
      screen.getByLabelText('Votre question'),
      'Comment valider une contremarque ?'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Envoyer' }))

    expect(api.postProAssistantMessage).toHaveBeenCalledWith({
      body: {
        message: 'Comment valider une contremarque ?',
        conversationId: null,
        offererId: 12,
        currentPath: '/offres',
      },
    })
    expect(
      await screen.findByText('Guichet', { selector: 'strong' })
    ).toBeInTheDocument()
    expect(
      within(screen.getByRole('list', { name: 'Aller à la page' })).getByRole(
        'link',
        { name: 'Guichet' }
      )
    ).toHaveAttribute('href', '/guichet')
    expect(
      within(
        screen.getByRole('list', { name: 'Pour aller plus loin' })
      ).getByRole('link', { name: /Comment valider une contremarque/ })
    ).toHaveAttribute('href', 'https://aide.passculture.app/hc/fr/articles/42')
    expect(mockLogEvent).toHaveBeenCalledWith(
      ProAssistantEvents.SENT_PRO_ASSISTANT_MESSAGE,
      { isNewConversation: true }
    )
  })

  it('should continue the conversation with the conversation id', async () => {
    renderProAssistant()
    await userEvent.click(
      screen.getByRole('button', { name: 'Demander à Culturo' })
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Où voir mes remboursements ?' })
    )
    await screen.findByRole('link', { name: 'Guichet' })

    await userEvent.type(screen.getByLabelText('Votre question'), 'Et après ?')
    await userEvent.click(screen.getByRole('button', { name: 'Envoyer' }))

    await waitFor(() =>
      expect(api.postProAssistantMessage).toHaveBeenLastCalledWith({
        body: expect.objectContaining({
          message: 'Et après ?',
          conversationId: 'a'.repeat(32),
        }),
      })
    )
  })

  it('should display the error message from the API', async () => {
    vi.spyOn(api, 'postProAssistantMessage').mockRejectedValue(
      makeApiError({
        status: 429,
        body: {
          global:
            'Vous avez posé beaucoup de questions. Merci de réessayer un peu plus tard.',
        },
      })
    )
    renderProAssistant()
    await userEvent.click(
      screen.getByRole('button', { name: 'Demander à Culturo' })
    )

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Comment créer une offre collective ?',
      })
    )

    expect(
      await screen.findByText(
        'Vous avez posé beaucoup de questions. Merci de réessayer un peu plus tard.'
      )
    ).toBeInTheDocument()
  })

  it('should clear the field and keep the focus in it after sending', async () => {
    renderProAssistant()
    await userEvent.click(
      screen.getByRole('button', { name: 'Demander à Culturo' })
    )
    const field = screen.getByLabelText('Votre question')

    await userEvent.type(field, 'Comment valider une contremarque ?')
    await userEvent.click(screen.getByRole('button', { name: 'Envoyer' }))

    expect(field).toHaveValue('')
    expect(field).toHaveFocus()
    expect(await screen.findByText('0/500')).toBeInTheDocument()
  })

  it('should send the question with the Enter key', async () => {
    renderProAssistant()
    await userEvent.click(
      screen.getByRole('button', { name: 'Demander à Culturo' })
    )

    await userEvent.type(
      screen.getByLabelText('Votre question'),
      'Comment valider une contremarque ?{Enter}'
    )

    expect(api.postProAssistantMessage).toHaveBeenCalledWith({
      body: expect.objectContaining({
        message: 'Comment valider une contremarque ?',
      }),
    })
    expect(screen.getByLabelText('Votre question')).toHaveValue('')
  })

  it.each(['Shift', 'Alt'])(
    'should add a line break with %s + Enter without sending',
    async (modifier) => {
      renderProAssistant()
      await userEvent.click(
        screen.getByRole('button', { name: 'Demander à Culturo' })
      )
      const field = screen.getByLabelText('Votre question')

      await userEvent.type(
        field,
        `Bonjour{${modifier}>}{Enter}{/${modifier}}merci`
      )

      expect(field).toHaveValue('Bonjour\nmerci')
      expect(api.postProAssistantMessage).not.toHaveBeenCalled()
    }
  )

  it('should move the focus from the field to the send button', async () => {
    renderProAssistant()
    await userEvent.click(
      screen.getByRole('button', { name: 'Demander à Culturo' })
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Comment valider une contremarque ?' })
    )
    await screen.findByRole('link', { name: 'Guichet' })

    await userEvent.type(screen.getByLabelText('Votre question'), 'Et après ?')
    await userEvent.tab()

    expect(screen.getByRole('button', { name: 'Envoyer' })).toHaveFocus()
  })

  it('should show that Culturo is thinking while waiting for the answer', async () => {
    let resolveAnswer: (value: PostProAssistantMessageResponseModel) => void =
      () => {}
    vi.spyOn(api, 'postProAssistantMessage').mockReturnValue(
      new Promise((resolve) => {
        resolveAnswer = resolve
      })
    )
    const { container } = renderProAssistant()
    await userEvent.click(
      screen.getByRole('button', { name: 'Demander à Culturo' })
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Comment valider une contremarque ?' })
    )

    expect(screen.getByText('Culturo réfléchit…')).toBeInTheDocument()
    expect(await axe(container)).toHaveNoViolations()

    resolveAnswer(answer)

    expect(
      await screen.findByRole('link', { name: 'Guichet' })
    ).toBeInTheDocument()
    expect(screen.queryByText('Culturo réfléchit…')).not.toBeInTheDocument()
  })

  it('should start a new conversation', async () => {
    renderProAssistant()
    await userEvent.click(
      screen.getByRole('button', { name: 'Demander à Culturo' })
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Comment valider une contremarque ?' })
    )
    await screen.findByRole('link', { name: 'Guichet' })

    await userEvent.click(
      screen.getByRole('button', { name: 'Nouvelle conversation' })
    )

    expect(
      screen.queryByRole('link', { name: 'Guichet' })
    ).not.toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Comment valider une contremarque ?' })
    ).toBeInTheDocument()
  })
})
