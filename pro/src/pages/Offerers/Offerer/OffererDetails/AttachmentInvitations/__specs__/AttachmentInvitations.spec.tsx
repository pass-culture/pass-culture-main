import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { api } from 'apiClient/api'
import { ApiError, OffererMemberStatus } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'
import Notification from 'components/Notification/Notification'
import * as useAnalytics from 'hooks/useAnalytics'
import AttachmentInvitations from 'pages/Offerers/Offerer/OffererDetails/AttachmentInvitations/AttachmentInvitations'
import { renderWithProviders } from 'utils/renderWithProviders'

vi.mock('apiClient/api', () => ({
  api: {
    getOffererMembers: vi.fn(),
    inviteMember: vi.fn(),
  },
}))

const mockLogEvent = vi.fn()

const renderAttachmentInvitations = () => {
  renderWithProviders(
    <>
      <AttachmentInvitations offererId={1} />
      <Notification />
    </>
  )
}

describe('AttachmentInvitations', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getOffererMembers').mockResolvedValueOnce({ members: [] })
    waitFor(() => {
      expect(api.getOffererMembers).toHaveBeenCalled()
    })

    vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('The user should see a button to display the invite form', async () => {
    renderAttachmentInvitations()
    expect(screen.getByText('Ajouter un collaborateur')).toBeInTheDocument()
    expect(
      screen.queryByText(
        /Vous pouvez inviter des collaborateurs à rejoindre votre espace/
      )
    ).not.toBeInTheDocument()

    expect(
      screen.queryByRole('button', { name: 'Voir moins de collaborateurs' })
    ).not.toBeInTheDocument()
  })

  it('Should display the invite form on click', async () => {
    renderAttachmentInvitations()
    await userEvent.click(screen.getByText('Ajouter un collaborateur'))
    expect(
      screen.queryByText('Ajouter un collaborateur')
    ).not.toBeInTheDocument()
    expect(
      screen.getByText(
        /Vous pouvez inviter des collaborateurs à rejoindre votre espace/
      )
    ).toBeInTheDocument()
  })

  it('Should display the form error on invalid email', async () => {
    renderAttachmentInvitations()
    await userEvent.click(screen.getByText('Ajouter un collaborateur'))
    await userEvent.type(await screen.getByLabelText('Adresse email'), '123456')
    await userEvent.click(screen.getByText('Inviter'))
    expect(
      screen.getByText(/Veuillez renseigner un email valide/)
    ).toBeInTheDocument()
  })

  it('Should display add the email on success and trigger buttons event', async () => {
    renderAttachmentInvitations()
    await userEvent.click(screen.getByText('Ajouter un collaborateur'))

    expect(mockLogEvent).toHaveBeenCalledWith('hasClickedAddCollaborator', {
      offererId: 1,
    })
    expect(mockLogEvent).toHaveBeenCalledTimes(1)

    await userEvent.type(
      await screen.getByLabelText('Adresse email'),
      'test@test.fr'
    )
    await userEvent.click(screen.getByText('Inviter'))

    await waitFor(() => {
      expect(
        screen.getByText(/L'invitation a bien été envoyée/)
      ).toBeInTheDocument()
    })

    expect(mockLogEvent).toHaveBeenCalledWith('hasSentInvitation', {
      offererId: 1,
    })

    expect(mockLogEvent).toHaveBeenCalledTimes(2)

    expect(screen.getByText('test@test.fr')).toBeInTheDocument()
  })

  it('Should display error message', async () => {
    renderAttachmentInvitations()
    await userEvent.click(screen.getByText('Ajouter un collaborateur'))

    await userEvent.type(
      await screen.getByLabelText('Adresse email'),
      'test@test.fr'
    )

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

    await userEvent.click(screen.getByText('Inviter'))

    await waitFor(() => {
      expect(
        screen.getByText(/Une invitation a déjà été envoyée à ce collaborateur/)
      ).toBeInTheDocument()
    })
  })

  it('should display button to show all members', async () => {
    vi.spyOn(api, 'getOffererMembers').mockResolvedValue({
      members: [
        { email: 'email1@gmail.com', status: OffererMemberStatus.VALIDATED },
        { email: 'email2@gmail.com', status: OffererMemberStatus.VALIDATED },
        { email: 'email3@gmail.com', status: OffererMemberStatus.VALIDATED },
        { email: 'email4@gmail.com', status: OffererMemberStatus.PENDING },
        { email: 'email5@gmail.com', status: OffererMemberStatus.PENDING },
        { email: 'email6@gmail.com', status: OffererMemberStatus.PENDING },
      ],
    })

    renderAttachmentInvitations()

    await waitFor(() => {
      expect(screen.getByText('email1@gmail.com')).toBeInTheDocument()
    })

    expect(screen.getAllByText(/Validé/)).toHaveLength(3)
    expect(screen.getAllByText(/En attente/)).toHaveLength(2)

    expect(
      screen.getByRole('button', { name: 'Voir plus de collaborateurs' })
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText('Voir plus de collaborateurs'))

    expect(screen.getAllByText(/En attente/)).toHaveLength(3)

    expect(
      screen.getByRole('button', { name: 'Voir moins de collaborateurs' })
    ).toBeInTheDocument()
  })
})
