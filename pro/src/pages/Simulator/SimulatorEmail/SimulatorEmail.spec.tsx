import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useNavigate } from 'react-router'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { serializeApiErrors } from '@/apiClient/helpers'
import { ActivityNotOpenToPublic, TargetAudience } from '@/apiClient/v1'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { sendSentryCustomError } from '@/commons/utils/sendSentryCustomError'

import { SimulatorContext } from '../SimulatorContext'
import { SimulatorEmail } from './SimulatorEmail'

vi.mock('@/apiClient/api', () => ({
  api: {
    sendSignupSimulationSummary: vi.fn(),
  },
}))

vi.mock('@/commons/utils/sendSentryCustomError', () => ({
  sendSentryCustomError: vi.fn(),
}))

vi.mock('@/apiClient/helpers', async () => ({
  ...(await vi.importActual<typeof import('@/apiClient/helpers')>(
    '@/apiClient/helpers'
  )),
  serializeApiErrors: vi.fn(),
}))

vi.mock('@/commons/hooks/useSnackBar', () => ({
  useSnackBar: vi.fn(),
}))

vi.mock('react-router', async () => ({
  ...(await vi.importActual('react-router')),
  useNavigate: vi.fn(),
}))

const mockNavigate = vi.fn()
const mockSnackBarError = vi.fn()

const contextValue = {
  openToPublic: 'true',
  setOpenToPublic: vi.fn(),
  activity: ActivityNotOpenToPublic.ARTISTIC_COMPANY,
  setActivity: vi.fn(),
  siret: '123 456 789 00012',
  setSiret: vi.fn(),
  targetAudiences: { individual: true, collective: false },
  setTargetAudiences: vi.fn(),
}

const renderSimulatorEmail = (contextOverride = {}) => {
  return renderWithProviders(
    <SimulatorContext.Provider value={{ ...contextValue, ...contextOverride }}>
      <SimulatorEmail />
    </SimulatorContext.Provider>,
    { features: ['WIP_PRE_SIGNUP_SIMULATION'] }
  )
}

const fillAndSubmit = async (email: string) => {
  const user = userEvent.setup()
  if (email) {
    await user.type(screen.getByLabelText('Adresse email'), email)
  }
  await user.click(screen.getByRole('button', { name: 'Recevoir la liste' }))
}

beforeEach(() => {
  vi.clearAllMocks()
  vi.mocked(useNavigate).mockReturnValue(mockNavigate)
  vi.mocked(useSnackBar).mockReturnValue({
    error: mockSnackBarError,
    success: vi.fn(),
  })
})

describe('<SimulatorEmail />', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderWithProviders(<SimulatorEmail />)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('renders the email field and the submit button', () => {
    renderSimulatorEmail()

    expect(screen.getByLabelText('Adresse email')).toBeVisible()
    expect(
      screen.getByRole('button', { name: 'Recevoir la liste' })
    ).toBeVisible()
  })

  it('shows a validation error and does not call the API when the email is empty', async () => {
    renderSimulatorEmail()

    await fillAndSubmit('')

    expect(
      await screen.findByText('Veuillez renseigner une adresse email')
    ).toBeVisible()
    expect(api.sendSignupSimulationSummary).not.toHaveBeenCalled()
  })

  it('calls the API with the collected data and navigates to the confirmation page on success', async () => {
    vi.mocked(api.sendSignupSimulationSummary).mockResolvedValueOnce(
      null as never
    )

    renderSimulatorEmail()

    await fillAndSubmit('test@example.com')

    expect(api.sendSignupSimulationSummary).toHaveBeenCalledWith({
      body: {
        isOpenToPublic: true,
        activity: ActivityNotOpenToPublic.ARTISTIC_COMPANY,
        siret: '12345678900012',
        targets: [TargetAudience.INDIVIDUAL],
        email: 'test@example.com',
      },
    })
    expect(mockNavigate).toHaveBeenCalledWith(
      '/inscription/preparation/email-confirmation'
    )
  })

  it('shows a generic error and does not call the API when a required simulator value is missing', async () => {
    renderSimulatorEmail({ siret: undefined })

    await fillAndSubmit('test@example.com')

    expect(mockSnackBarError).toHaveBeenCalledWith('Une erreur est survenue')
    expect(api.sendSignupSimulationSummary).not.toHaveBeenCalled()
  })

  it('serializes field errors returned by the API when the error status is below 500', async () => {
    const apiError = {
      status: 400,
      body: { email: 'Adresse invalide' },
      name: 'ApiError',
      message: 'API error',
    }
    vi.mocked(api.sendSignupSimulationSummary).mockRejectedValueOnce(apiError)

    renderSimulatorEmail()

    await fillAndSubmit('test@example.com')

    expect(serializeApiErrors).toHaveBeenCalledWith(
      apiError.body,
      expect.any(Function)
    )
    expect(mockSnackBarError).not.toHaveBeenCalled()
  })

  it('shows a generic error when the API error status is 500 or above', async () => {
    const apiError = {
      status: 500,
      body: {},
      name: 'ApiError',
      message: 'API error',
    }
    vi.mocked(api.sendSignupSimulationSummary).mockRejectedValueOnce(apiError)

    renderSimulatorEmail()

    await fillAndSubmit('test@example.com')

    expect(mockSnackBarError).toHaveBeenCalledWith('Une erreur est survenue')
    expect(sendSentryCustomError).toHaveBeenCalledWith(apiError)
    expect(serializeApiErrors).not.toHaveBeenCalled()
  })
})
