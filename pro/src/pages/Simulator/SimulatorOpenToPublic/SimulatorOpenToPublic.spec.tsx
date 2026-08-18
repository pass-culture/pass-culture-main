import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event/dist/cjs/index.js'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { SimulatorContext } from 'pages/Simulator/SimulatorContext'
import { SimulatorOpenToPublic } from 'pages/Simulator/SimulatorOpenToPublic/SimulatorOpenToPublic'
import * as router from 'react-router'
import { axe } from 'vitest-axe'

import { noop } from '@/commons/utils/noop'

const mockSetOpenToPublic = vi.fn()
const contextValue = {
  siret: undefined,
  setSiret: noop,
  targetAudiences: {
    individual: undefined,
    collective: undefined,
  },
  setTargetAudiences: vi.fn(),
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

vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router')
  return {
    ...actual,
    useNavigate: vi.fn(),
  }
})

describe('<SimulatorOpenToPublic />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderSimulatorOpenToPublic()

    expect(await axe(container)).toHaveNoViolations()
  })
  it('should save the form value and navigate', async () => {
    const mockNavigate = vi.fn()
    vi.mocked(router.useNavigate).mockReturnValue(mockNavigate)
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
