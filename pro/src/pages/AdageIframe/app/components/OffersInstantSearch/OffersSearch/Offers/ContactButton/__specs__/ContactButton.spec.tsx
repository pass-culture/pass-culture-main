import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { AdageFrontRoles } from 'apiClient/adage'
import { renderWithProviders } from 'utils/renderWithProviders'

import ContactButton, { IContactButtonProps } from '../ContactButton'

const renderContactButton = (
  props: IContactButtonProps,
  features?: { list: { isActive: true; nameKey: string }[] }
) => {
  const storeOverrides = {
    features: features,
  }
  return renderWithProviders(<ContactButton {...props} />, {
    storeOverrides: storeOverrides,
  })
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
    venueName: 'Mon lieu',
    offererName: 'Ma structure',
    userRole: AdageFrontRoles.REDACTOR,
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
  it('should display request form on click if ff active', async () => {
    renderContactButton(defaultProps, {
      list: [{ isActive: true, nameKey: 'WIP_ENABLE_COLLECTIVE_REQUEST' }],
    })

    const contactButton = screen.getByRole('button', { name: 'Contacter' })
    await userEvent.click(contactButton)

    expect(screen.getByText('Mon lieu - Ma structure')).toBeInTheDocument()
  })
})
