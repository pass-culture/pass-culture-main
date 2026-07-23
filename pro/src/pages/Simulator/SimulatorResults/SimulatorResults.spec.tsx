import { screen, waitFor } from '@testing-library/react'
import { noop } from 'commons/utils/noop'
import { SimulatorContext } from 'pages/Simulator/SimulatorContext'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  ActivityNotOpenToPublic,
  ContentMessageSignupSimulation,
  EligibilityDocuments,
  ImportanceLevelMessageSignupSimulation,
} from 'apiClient/v1'
import { SimulatorResults } from './SimulatorResults'

const contextValue = {
  siret: '123 456 789 01234',
  setSiret: vi.fn(),
  targetCustomer: {
    individual: true,
    educational: true,
  },
  setTargetCustomer: vi.fn(),
  openToPublic: 'true',
  setOpenToPublic: noop,
  activity: ActivityNotOpenToPublic.ARTISTIC_COMPANY,
  setActivity: vi.fn(),
}

const renderSimulatorResult = () => {
  return renderWithProviders(
    <SimulatorContext.Provider value={contextValue}>
      <SimulatorResults />
    </SimulatorContext.Provider>,
    { features: ['WIP_PRE_SIGNUP_SIMULATION'] }
  )
}

describe('<SimulatorResults />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<SimulatorResults />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render with document and message', async () => {
    vi.spyOn(api, 'signupSimulation').mockResolvedValueOnce({
      eligibilityDocuments: [EligibilityDocuments.PRICES],
      messages: [
        {
          content: ContentMessageSignupSimulation.BOOKSTORE,
          importanceLevel: ImportanceLevelMessageSignupSimulation.ALERT,
        },
      ],
    })
    renderSimulatorResult()

    await waitFor(() => {
      expect(screen.getByText('Grille tarifaire')).toBeVisible()
    })
  })
})
