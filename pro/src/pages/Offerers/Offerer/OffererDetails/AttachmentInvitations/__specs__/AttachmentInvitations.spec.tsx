import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import Notification from 'components/Notification/Notification'
import AttachmentInvitations from 'pages/Offerers/Offerer/OffererDetails/AttachmentInvitations/AttachmentInvitations'
import { renderWithProviders } from 'utils/renderWithProviders'

const renderAttachmentInvitations = () => {
  renderWithProviders(
    <>
      <AttachmentInvitations offererId={1} />
      <Notification />
    </>
  )
}

describe('AttachmentInvitations', () => {
  it('The user should see a button to display the invite form', async () => {
    renderAttachmentInvitations()
    expect(screen.getByText('Ajouter un collaborateur')).toBeInTheDocument()
    expect(
      screen.queryByText(
        /Vous pouvez inviter des collaborateurs à rejoindre votre espace/
      )
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

  it('Should display add the email on success', async () => {
    renderAttachmentInvitations()
    await userEvent.click(screen.getByText('Ajouter un collaborateur'))
    await userEvent.type(
      await screen.getByLabelText('Adresse email'),
      'test@test.fr'
    )
    await userEvent.click(screen.getByText('Inviter'))
    expect(
      screen.getByText(/L'invitation a bien été envoyée/)
    ).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText('test@test.fr')).toBeInTheDocument()
    })
  })
})
