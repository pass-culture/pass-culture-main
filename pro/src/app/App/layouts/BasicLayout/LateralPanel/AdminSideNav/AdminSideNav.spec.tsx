import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { AdminSideNavLinks } from './AdminSideNav'

const renderAdminSideNav = (props = {}) =>
  renderWithProviders(<AdminSideNavLinks {...props} />)

describe('AdminSideNav', () => {
  it('should toggle the data section on button click', async () => {
    renderAdminSideNav()
    const button = screen.getByRole('button', { name: /Données d’activité/ })
    expect(screen.getByText('Individuel')).toBeInTheDocument()
    await userEvent.click(button)
    expect(screen.queryByText('Individuel')).not.toBeInTheDocument()
    await userEvent.click(button)
    expect(screen.getByText('Individuel')).toBeInTheDocument()
  })

  it('should open the dropdown menu when Centre d’aide is clicked', async () => {
    renderAdminSideNav()
    const helpButton = screen.getByRole('button', { name: /Centre d’aide/ })
    await userEvent.click(helpButton)
    expect(screen.getByText('Centre d’aide')).toBeInTheDocument()
    expect(screen.getByText(/Contacter nos équipes/)).toBeInTheDocument()
  })
})
