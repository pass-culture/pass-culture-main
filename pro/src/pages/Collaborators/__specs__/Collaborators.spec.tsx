import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient/api'
import { ApiError, OffererMemberStatus } from '@/apiClient/v1'
import type { ApiRequestOptions } from '@/apiClient/v1/core/ApiRequestOptions'
import type { ApiResult } from '@/apiClient/v1/core/ApiResult'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

import { Component as Collaborators } from '../Collaborators'

vi.mock('@/apiClient/api', () => ({
  api: {
    getOffererMembers: vi.fn(),
    inviteMember: vi.fn(),
  },
}))

const mockLogEvent = vi.fn()

const offererNamesValidated = [
  {
    ...defaultGetOffererResponseModel,
    id: 1,
    name: 'Offerer 1',
  },
]

const renderCollaborators = async (options?: RenderWithProvidersOptions) => {
  await renderWithProviders(
    <>
      <Collaborators />
      <SnackBarContainer />
    </>,
    {
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
          selectedAdminOfferer: { id: 1 },
        },
        offerer: {
          offererNamesValidated,
          offererNames: offererNamesValidated,
        },
      },
      ...options,
    }
  )
}

describe('Collaborators', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOffererMembers').mockResolvedValue({ members: [] })

    vi.spyOn(api, 'inviteMember').mockResolvedValue(undefined)

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))
  })

  it('should display a button to open invite form', async () => {
    await renderCollaborators()

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
    await renderCollaborators()

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
    await renderCollaborators()

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
    await renderCollaborators()

    await userEvent.click(
      screen.getByRole('button', { name: 'Ajouter un collaborateur' })
    )

    expect(mockLogEvent).toHaveBeenCalledWith('hasClickedAddCollaborator', {
      offererId: 1,
    })

    await userEvent.type(screen.getByLabelText('Adresse email'), 'test@test.fr')

    await userEvent.click(
      screen.getByRole('button', { name: 'Inviter le collaborateur' })
    )

    await waitFor(() => {
      expect(
        screen.getByText(/L'invitation a bien été envoyée/)
      ).toBeInTheDocument()
    })

    expect(mockLogEvent).toHaveBeenCalledWith('hasSentInvitation', {
      offererId: 1,
    })

    expect(screen.getByText('test@test.fr')).toBeInTheDocument()
  })

  it('should display api email error message', async () => {
    vi.spyOn(api, 'inviteMember').mockRejectedValue(
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

    await renderCollaborators()

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
    vi.spyOn(api, 'inviteMember').mockRejectedValue({})

    await renderCollaborators()

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
    vi.spyOn(api, 'getOffererMembers').mockResolvedValue({
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

    await renderCollaborators()

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
    vi.spyOn(api, 'getOffererMembers').mockResolvedValue({
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

    await renderCollaborators()

    expect(await screen.findByText('validated@test.fr')).toBeInTheDocument()
    expect(screen.getByText('pending@test.fr')).toBeInTheDocument()

    expect(screen.getByText('Validé')).toBeInTheDocument()
    expect(screen.getByText('En attente')).toBeInTheDocument()
  })

  it('should hide show-more button when members count is exactly 10', async () => {
    vi.spyOn(api, 'getOffererMembers').mockResolvedValue({
      members: Array.from({ length: 10 }, (_, index) => ({
        email: `user${index}@test.fr`,
        status: OffererMemberStatus.VALIDATED,
      })),
    })

    await renderCollaborators()

    expect(await screen.findByText('user0@test.fr')).toBeInTheDocument()

    expect(
      screen.queryByRole('button', {
        name: 'Voir plus de collaborateurs',
      })
    ).not.toBeInTheDocument()
  })
})
