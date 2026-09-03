import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { CancelablePromise } from '@/apiClient/compat'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { ReSendEmailCallout } from '@/components/ReSendEmailCallout/ReSendEmailCallout'
import { SnackBarContainer } from '@/components/SnackBarContainer/SnackBarContainer'

const renderComponent = (
  action: () => CancelablePromise<void> = () =>
    new CancelablePromise<void>((resolve) => resolve())
) =>
  renderWithProviders(
    <>
      <SnackBarContainer />
      <ReSendEmailCallout action={action} />
    </>
  )

describe('ReSendEmailCallout', () => {
  it('should render correctly', () => {
    renderComponent()
    expect(screen.getAllByRole('status')[0]).toHaveTextContent(
      /Email non reçu ?/
    )
    expect(
      screen.getByRole('button', { name: 'Renvoyer un nouveau lien' })
    ).toBeEnabled()
  })

  it('should display a notification on action success', async () => {
    renderComponent()
    await userEvent.click(
      screen.getByRole('button', { name: 'Renvoyer un nouveau lien' })
    )

    expect(screen.getAllByText('Email envoyé.').length).toBeGreaterThan(0)
  })

  it('should display an error on action failure', async () => {
    renderComponent(
      () =>
        new CancelablePromise<void>((_resolve, reject) =>
          reject(new Error('error'))
        )
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Renvoyer un nouveau lien' })
    )

    expect(
      screen.getAllByText(
        'Une erreur est survenue, veuillez réessayer ultérieurement.'
      ).length
    ).toBeGreaterThan(0)
  })
})
