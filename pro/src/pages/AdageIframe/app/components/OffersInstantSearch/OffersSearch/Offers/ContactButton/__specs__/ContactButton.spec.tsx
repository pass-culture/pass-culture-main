import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import ContactButton, { IContactButtonProps } from '../ContactButton'

const renderContactButton = (props: IContactButtonProps) => {
  return renderWithProviders(<ContactButton {...props} />)
}
jest.mock('apiClient/api', () => ({
  apiAdage: {
    logContactModalButtonClick: jest.fn(),
  },
}))

jest.mock('pages/AdageIframe/libs/initAlgoliaAnalytics')

describe('ContactButton', () => {
  const defaultProps = {
    offerId: 1,
    position: 1,
    queryId: 'test',
  }
  it('should display modal on click', async () => {
    renderContactButton(defaultProps)
    const contactButton = screen.getByRole('button', { name: 'Contacter' })
    await userEvent.click(contactButton)

    expect(
      screen.getByText(
        /Afin de personnaliser cette offre, nous vous invitons à entrer en contact avec votre partenaire culturel :/
      )
    ).toBeInTheDocument()
  })

  it('should close modal on click', async () => {
    renderContactButton(defaultProps)

    const contactButton = screen.getByRole('button', { name: 'Contacter' })
    await userEvent.click(contactButton)

    const closeButton = screen.getByRole('button', { name: 'Fermer' })
    await userEvent.click(closeButton)

    expect(
      screen.queryByText(
        /Afin de personnaliser cette offre, nous vous invitons à entrer en contact avec votre partenaire culturel :/
      )
    ).not.toBeInTheDocument()
  })
})
