import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { noop } from 'commons/utils/noop'
import * as router from 'react-router'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { SimulatorContext } from '@/pages/Simulator/SimulatorContext'

import { SimulatorSiret } from './SimulatorSiret'

const setSiretMock = vi.fn()
const contextValue = {
  siret: undefined,
  setSiret: setSiretMock,
  targetAudiences: {
    individual: undefined,
    collective: undefined,
  },
  setTargetAudiences: vi.fn(),
  openToPublic: null,
  setOpenToPublic: noop,
  activity: undefined,
  setActivity: vi.fn(),
}
const renderSimulatorSiret = () => {
  return renderWithProviders(
    <SimulatorContext.Provider value={contextValue}>
      <SimulatorSiret />
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

describe('<SimulatorSiret />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderSimulatorSiret()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should save the siret on submit', async () => {
    const mockNavigate = vi.fn()
    vi.mocked(router.useNavigate).mockReturnValue(mockNavigate)
    renderSimulatorSiret()

    await userEvent.type(
      screen.getByLabelText(/Numéro de SIRET/),
      '11111111111111'
    )

    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    expect(setSiretMock).toHaveBeenCalled()
    expect(mockNavigate).toHaveBeenCalledWith(
      '/inscription/preparation/accueil-public'
    )
  })
})
