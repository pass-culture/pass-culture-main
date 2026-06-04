import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event/dist/cjs/index.js'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { SimulatorContext } from 'pages/Simulator/SimulatorContext'
import { SimulatorOpenToPublic } from 'pages/Simulator/SimulatorOpenToPublic/SimulatorOpenToPublic'
import { axe } from 'vitest-axe'

import { noop } from '@/commons/utils/noop'

const mockSetOpenToPublic = vi.fn()
const contextValue = {
  siret: undefined,
  setSiret: noop,
  targetCustomer: {
    individual: undefined,
    educational: undefined,
  },
  setTargetCustomer: vi.fn(),
  openToPublic: null,
  setOpenToPublic: mockSetOpenToPublic,
  activity: undefined,
  setActivity: vi.fn(),
}
const renderSimulatorOpenToPublic = () => {
  return renderWithProviders(
    <SimulatorContext.Provider value={contextValue}>
      <SimulatorOpenToPublic />
    </SimulatorContext.Provider>,
    { features: ['WIP_PRE_SIGNUP_SIMULATION'] }
  )
}

describe('<SimulatorOpenToPublic />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderSimulatorOpenToPublic()

    expect(await axe(container)).toHaveNoViolations()
  })
  it('should save the form value and navigate', async () => {
    const mockNavigate = vi.fn()
    vi.spyOn(await import('react-router'), 'useNavigate').mockReturnValue(
      mockNavigate
    )
    renderSimulatorOpenToPublic()

    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    expect(mockSetOpenToPublic).not.toHaveBeenCalled()
    expect(screen.getByRole('alert')).toHaveTextContent(
      /Veuillez sélectionner une option/
    )

    await userEvent.click(screen.getByRole('radio', { name: /Oui/ }))

    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    expect(mockSetOpenToPublic).toHaveBeenCalledWith('true')
    expect(mockNavigate).toHaveBeenCalledWith(
      '/inscription/preparation/activite'
    )
  })
})
