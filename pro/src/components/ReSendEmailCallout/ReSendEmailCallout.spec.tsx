import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { CancelablePromise } from '@/apiClient/v1'
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
    expect(screen.getByText(/Email non reçu ?/)).toBeInTheDocument()
    expect(screen.getByText('cliquez ici')).toBeEnabled()
  })

  it('should display a notification on action success', async () => {
    renderComponent()
    await userEvent.click(screen.getByText('cliquez ici'))

    expect(screen.getByText('Email envoyé.')).toBeInTheDocument()
  })

  it('should display a notification on action success', async () => {
    renderComponent(
      () =>
        new CancelablePromise<void>((_resolve, reject) =>
          reject(new Error('error'))
        )
    )
    await userEvent.click(screen.getByText('cliquez ici'))

    expect(
      screen.getByText(
        'Une erreur est survenue, veuillez réessayer ultérieurement.'
      )
    ).toBeInTheDocument()
  })
})
