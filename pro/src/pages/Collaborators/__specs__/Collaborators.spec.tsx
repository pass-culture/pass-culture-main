import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { apiNew } from '@/apiClient/api'
import {
  ApiError,
  type ApiRequestOptions,
  type ApiResult,
} from '@/apiClient/compat'
import { OffererMemberStatus } from '@/apiClient/v1/new'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { Component as Collaborators } from '../Collaborators'

vi.mock('@/apiClient/api', () => ({
  apiNew: {
    getOffererMembers: vi.fn(),
    inviteMember: vi.fn(),
  },
}))

const mockLogEvent = vi.fn()

const offererNames = [
  {
    id: 1,
    name: 'Offerer 1',
    validated: true,
  },
]

const renderCollaborators = (options?: RenderWithProvidersOptions) => {
  renderWithProviders(
    <>
      <Collaborators />
      <SnackBarContainer />
    </>,
    {
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
          selectedAdminOfferer: { id: 1 },
          offererNames: offererNames,
        },
      },
      ...options,
    }
  )
}

describe('Collaborators', () => {
  beforeEach(() => {
    vi.spyOn(apiNew, 'getOffererMembers').mockResolvedValue({ members: [] })

    vi.spyOn(apiNew, 'inviteMember').mockResolvedValue(undefined)

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should display a button to open invite form', () => {
    renderCollaborators()

    expect(
      screen.getByRole('button', { name: 'Ajouter un collaborateur' })
    ).toBeInTheDocument()

    expect(
      screen.queryByText(
        /Vous pouvez inviter des collaborateurs à rejoindre votre espace/
      )
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole('button', {
        name: 'Voir moins de collaborateurs',
      })
    ).not.toBeInTheDocument()
  })

  it('should display the invite form on click', async () => {
    renderCollaborators()

    await userEvent.click(
      screen.getByRole('button', { name: 'Ajouter un collaborateur' })
    )

    expect(
      screen.getByText(
        /Vous pouvez inviter des collaborateurs à rejoindre votre espace/
      )
    ).toBeInTheDocument()
  })

  it('should display validation error on invalid email', async () => {
    renderCollaborators()

    await userEvent.click(
      screen.getByRole('button', { name: 'Ajouter un collaborateur' })
    )

    await userEvent.type(screen.getByLabelText('Adresse email'), '123456')

    await userEvent.click(
      screen.getByRole('button', { name: 'Inviter le collaborateur' })
    )

    expect(
      screen.getByText(/Veuillez renseigner un email valide/)
    ).toBeInTheDocument()
  })

  it('should invite collaborator successfully, log events and display email', async () => {
    renderCollaborators()

    await userEvent.click(
      screen.getByRole('button', { name: 'Ajouter un collaborateur' })
    )

    expect(mockLogEvent).toHaveBeenCalledWith('hasClickedAddCollaborator')

    await userEvent.type(screen.getByLabelText('Adresse email'), 'test@test.fr')

    await userEvent.click(
      screen.getByRole('button', { name: 'Inviter le collaborateur' })
    )

    await waitFor(() => {
      expect(
        screen.getByText(/L'invitation a bien été envoyée/)
      ).toBeInTheDocument()
    })

    expect(mockLogEvent).toHaveBeenCalledWith('hasSentInvitation')

    expect(screen.getByText('test@test.fr')).toBeInTheDocument()
  })

  it('should display api email error message', async () => {
    vi.spyOn(apiNew, 'inviteMember').mockRejectedValue(
      new ApiError(
        { method: 'POST' } as ApiRequestOptions,
        {
          status: 400,
          body: {
            email: 'Une invitation a déjà été envoyée à ce collaborateur',
          },
        } as ApiResult,
        ''
      )
    )

    renderCollaborators()

    await userEvent.click(
      screen.getByRole('button', { name: 'Ajouter un collaborateur' })
    )

    await userEvent.type(screen.getByLabelText('Adresse email'), 'test@test.fr')

    await userEvent.click(
      screen.getByRole('button', { name: 'Inviter le collaborateur' })
    )

    await waitFor(() => {
      expect(
        screen.getByText(/Une invitation a déjà été envoyée à ce collaborateur/)
      ).toBeInTheDocument()
    })
  })

  it('should display default error message on server error', async () => {
    vi.spyOn(apiNew, 'inviteMember').mockRejectedValue({})

    renderCollaborators()

    await userEvent.click(
      screen.getByRole('button', { name: 'Ajouter un collaborateur' })
    )

    await userEvent.type(screen.getByLabelText('Adresse email'), 'test@test.fr')

    await userEvent.click(
      screen.getByRole('button', { name: 'Inviter le collaborateur' })
    )

    await waitFor(() => {
      expect(
        screen.getByText(
          'Une erreur est survenue lors de l’envoi de l’invitation.'
        )
      ).toBeInTheDocument()
    })
  })
})

describe('ViewAllList', () => {
  it('should display button to show all members', async () => {
    vi.spyOn(apiNew, 'getOffererMembers').mockResolvedValue({
      members: [
        { email: 'email1@gmail.com', status: OffererMemberStatus.VALIDATED },
        { email: 'email2@gmail.com', status: OffererMemberStatus.VALIDATED },
        { email: 'email3@gmail.com', status: OffererMemberStatus.VALIDATED },
        { email: 'email7@gmail.com', status: OffererMemberStatus.VALIDATED },
        { email: 'email8@gmail.com', status: OffererMemberStatus.VALIDATED },
        { email: 'email9@gmail.com', status: OffererMemberStatus.VALIDATED },
        { email: 'email10@gmail.com', status: OffererMemberStatus.VALIDATED },
        { email: 'email12@gmail.com', status: OffererMemberStatus.VALIDATED },
        { email: 'email4@gmail.com', status: OffererMemberStatus.PENDING },
        { email: 'email5@gmail.com', status: OffererMemberStatus.PENDING },
        { email: 'email6@gmail.com', status: OffererMemberStatus.PENDING },
        { email: 'email11@gmail.com', status: OffererMemberStatus.VALIDATED },
        { email: 'email13@gmail.com', status: OffererMemberStatus.VALIDATED },
        { email: 'email14@gmail.com', status: OffererMemberStatus.VALIDATED },
      ],
    })

    renderCollaborators()

    await waitFor(() => {
      expect(screen.getByText('email1@gmail.com')).toBeInTheDocument()
    })

    expect(screen.getAllByText(/Validé/)).toHaveLength(8)
    expect(screen.getAllByText(/En attente/)).toHaveLength(2)

    expect(
      screen.getByRole('button', {
        name: 'Voir plus de collaborateurs',
      })
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Voir plus de collaborateurs',
      })
    )

    expect(screen.getAllByText(/En attente/)).toHaveLength(3)

    expect(
      screen.getByRole('button', {
        name: 'Voir moins de collaborateurs',
      })
    ).toBeInTheDocument()
  })

  it('should display validated and pending statuses correctly', async () => {
    vi.spyOn(apiNew, 'getOffererMembers').mockResolvedValue({
      members: [
        {
          email: 'validated@test.fr',
          status: OffererMemberStatus.VALIDATED,
        },
        {
          email: 'pending@test.fr',
          status: OffererMemberStatus.PENDING,
        },
      ],
    })

    renderCollaborators()

    expect(await screen.findByText('validated@test.fr')).toBeInTheDocument()
    expect(screen.getByText('pending@test.fr')).toBeInTheDocument()

    expect(screen.getByText('Validé')).toBeInTheDocument()
    expect(screen.getByText('En attente')).toBeInTheDocument()
  })

  it('should hide show-more button when members count is exactly 10', async () => {
    vi.spyOn(apiNew, 'getOffererMembers').mockResolvedValue({
      members: Array.from({ length: 10 }, (_, index) => ({
        email: `user${index}@test.fr`,
        status: OffererMemberStatus.VALIDATED,
      })),
    })

    renderCollaborators()

    expect(await screen.findByText('user0@test.fr')).toBeInTheDocument()

    expect(
      screen.queryByRole('button', {
        name: 'Voir plus de collaborateurs',
      })
    ).not.toBeInTheDocument()
  })
})
