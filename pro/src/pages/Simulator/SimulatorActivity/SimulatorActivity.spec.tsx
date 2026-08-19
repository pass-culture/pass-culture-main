import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event/dist/cjs/index.js'
import { noop } from 'commons/utils/noop'
import { SimulatorContext } from 'pages/Simulator/SimulatorContext'
import * as router from 'react-router'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SimulatorActivity } from './SimulatorActivity'

const mockSetActivity = vi.fn()
const contextValue = {
  siret: undefined,
  setSiret: noop,
  targetAudiences: {
    individual: undefined,
    collective: undefined,
  },
  setTargetAudiences: noop,
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

const defaultUseLocationValue = {
  state: { offer: '', queryId: '' },
  hash: '',
  key: '',
  pathname: '/accueil',
  search: '',
}

vi.mock('react-router', async () => {
  const actual = await vi.importActual('react-router')
  return {
    ...actual,
    useLocation: vi.fn(() => defaultUseLocationValue),
    useNavigate: vi.fn(),
  }
})

describe('<SimulatorActivity />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderSimulatorActivity()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should save the form value and navigate', async () => {
    const mockNavigate = vi.fn()
    vi.mocked(router.useNavigate).mockReturnValue(mockNavigate)
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
