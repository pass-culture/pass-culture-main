import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { CancelablePromise } from 'apiClient/v1'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { Notification } from 'components/Notification/Notification'
import { ReSendEmailCallout } from 'components/ReSendEmailCallout/ReSendEmailCallout'

const renderComponent = (
  action: () => CancelablePromise<any> = () =>
    new CancelablePromise<any>((resolve) => resolve({}))
) =>
  renderWithProviders(
    <>
      <Notification />
      <ReSendEmailCallout action={action} />
    </>
  )

describe('ReSendEmailCallout', () => {
  it('should render correctly', () => {
    renderComponent()
    expect(
      screen.getByText(/Vous n’avez pas reçu d’email ?/)
    ).toBeInTheDocument()
    expect(screen.getByText('cliquez ici')).toBeEnabled()
  })

  it('should display a notification on action success', async () => {
    renderComponent()
    await userEvent.click(screen.getByText('cliquez ici'))

    expect(screen.getByText('Email renvoyé !')).toBeInTheDocument()
  })

  it('should display a notification on action success', async () => {
    renderComponent(
      () =>
        new CancelablePromise<any>((resolve, reject) =>
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
