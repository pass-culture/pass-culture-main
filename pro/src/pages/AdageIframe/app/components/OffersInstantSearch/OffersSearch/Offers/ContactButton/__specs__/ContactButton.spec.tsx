import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { AdageFrontRoles } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import { ContactButton, ContactButtonProps } from '../ContactButton'

const renderContactButton = (
  props: ContactButtonProps,
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(<ContactButton {...props} />, options)
}
vi.mock('apiClient/api', () => ({
  apiAdage: {
    logContactModalButtonClick: vi.fn(),
    logRequestFormPopinDismiss: vi.fn(),
  },
}))

describe('ContactButton', () => {
  const defaultProps = {
    offerId: 1,
    queryId: 'test',
    userRole: AdageFrontRoles.REDACTOR,
    contactForm: 'form',
  }

  it('should call the tracking function when the contact dialog is closed', async () => {
    renderContactButton(defaultProps)

    const contactButton = screen.getByRole('button', {
      name: 'Contacter',
    })
    await userEvent.click(contactButton)

    const closeButton = screen.getByRole('button', { name: 'Annuler' })
    await userEvent.click(closeButton)

    expect(apiAdage.logRequestFormPopinDismiss).toBeCalledTimes(1)

    expect(
      screen.queryByText('Contacter le partenaire culturel')
    ).not.toBeInTheDocument()
  })

  it('should display the contact form when the contact modal is opened', async () => {
    renderContactButton(defaultProps)

    const contactButton = screen.getByRole('button', {
      name: 'Contacter',
    })
    await userEvent.click(contactButton)

    expect(
      screen.getByText('Vous souhaitez contacter ce partenaire ?')
    ).toBeInTheDocument()
  })
})
