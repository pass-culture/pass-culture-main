import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event/dist/cjs/index.js'
import { noop } from 'commons/utils/noop'
import { SimulatorContext } from 'pages/Simulator/SimulatorContext'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SimulatorActivity } from './SimulatorActivity'

const mockSetActivity = vi.fn()
const contextValue = {
  siret: undefined,
  setSiret: noop,
  targetCustomer: {
    individual: undefined,
    educational: undefined,
  },
  setTargetCustomer: noop,
  openToPublic: 'true',
  setOpenToPublic: noop,
  activity: undefined,
  setActivity: mockSetActivity,
}
const renderSimulatorActivity = () => {
  return renderWithProviders(
    <SimulatorContext.Provider value={contextValue}>
      <SimulatorActivity />
    </SimulatorContext.Provider>,
    { features: ['WIP_PRE_SIGNUP_SIMULATION'] }
  )
}

describe('<SimulatorActivity />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderSimulatorActivity()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should save the form value and navigate', async () => {
    const mockNavigate = vi.fn()
    vi.spyOn(await import('react-router'), 'useNavigate').mockReturnValue(
      mockNavigate
    )
    renderSimulatorActivity()

    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    expect(mockSetActivity).not.toHaveBeenCalled()
    expect(screen.getByRole('alert')).toHaveTextContent(/Activité non valide/)

    await userEvent.selectOptions(
      screen.getByLabelText(/Activité principale/),
      'FESTIVAL'
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))
    expect(mockSetActivity).toHaveBeenCalledWith('FESTIVAL')
    expect(mockNavigate).toHaveBeenCalledWith(
      '/inscription/preparation/publics'
    )
  })
})
