import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AdminSideNavLinks } from './AdminSideNavLinks'

const renderAdminSideNavLinks = (props = {}) =>
  renderWithProviders(
    <AdminSideNavLinks isLateralPanelOpen={true} {...props} />
  )

describe('AdminSideNavLinks', () => {
  it('should toggle the data section on button click', async () => {
    renderAdminSideNavLinks()
    const button = screen.getByRole('button', { name: /Données d’activité/ })
    expect(screen.getByText('Individuel')).toBeInTheDocument()
    await userEvent.click(button)
    expect(screen.queryByText('Individuel')).not.toBeInTheDocument()
    await userEvent.click(button)
    expect(screen.getByText('Individuel')).toBeInTheDocument()
  })
  it('should open the dropdown menu when Centre d’aide is clicked', async () => {
    renderAdminSideNavLinks()
    const helpButton = screen.getByRole('button', { name: /Centre d’aide/ })
    await userEvent.click(helpButton)
    expect(screen.getByText('Centre d’aide')).toBeInTheDocument()
    expect(screen.getByText(/Contacter nos équipes/)).toBeInTheDocument()
  })
})
