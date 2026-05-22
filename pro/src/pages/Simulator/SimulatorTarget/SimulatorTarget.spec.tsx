import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { SimulatorTarget } from './SimulatorTarget'

const mockNavigate = vi.fn()

vi.mock('react-router', async () => {
  return {
    ...(await vi.importActual('react-router')),
    useNavigate: () => mockNavigate,
  }
})

const renderSimulatorTarget = () => {
  return renderWithProviders(<SimulatorTarget />)
}

describe('<SimulatorTarget />', () => {
  beforeEach(() => {
    mockNavigate.mockClear()
    localStorageManager.removeItem(LOCAL_STORAGE_KEY.SIMULATOR_TARGET_CUSTOMER)
  })

  it('should render without accessibility violations', async () => {
    const { container } = renderSimulatorTarget()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render the page title and subtitle', () => {
    renderSimulatorTarget()

    expect(
      screen.getByText('Quels publics souhaitez-vous cibler ?')
    ).toBeInTheDocument()
    expect(
      screen.getByText(/nous vous orienterons vers le bon dispositif/)
    ).toBeInTheDocument()
  })

  it('should render the two checkbox options', () => {
    renderSimulatorTarget()

    expect(
      screen.getByRole('checkbox', {
        name: /Les jeunes via l’application pass Culture/,
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('checkbox', {
        name: /Les groupes scolaires via ADAGE/,
      })
    ).toBeInTheDocument()
  })

  it('should render a back link pointing to the activity step', () => {
    renderSimulatorTarget()

    const backLink = screen.getByRole('link', { name: 'Retour' })

    expect(backLink).toHaveAttribute(
      'href',
      '/inscription/preparation/activite'
    )
  })

  it('should display a validation error when submitting with no checkbox checked', async () => {
    renderSimulatorTarget()

    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    await waitFor(() => {
      expect(
        screen.getByText('Veuillez sélectionner au moins une option')
      ).toBeInTheDocument()
    })

    expect(mockNavigate).not.toHaveBeenCalled()
  })

  it('should navigate to results page when submitting with "individual" checked', async () => {
    renderSimulatorTarget()

    await userEvent.click(
      screen.getByRole('checkbox', {
        name: /Les jeunes via l’application pass Culture/,
      })
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(
        '/inscription/preparation/resultats'
      )
    })
  })

  it('should navigate to results page when submitting with "educational" checked', async () => {
    renderSimulatorTarget()

    await userEvent.click(
      screen.getByRole('checkbox', { name: /Les groupes scolaires via ADAGE/ })
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(
        '/inscription/preparation/resultats'
      )
    })
  })

  it('should navigate to results page when submitting with both checkboxes checked', async () => {
    renderSimulatorTarget()

    await userEvent.click(
      screen.getByRole('checkbox', {
        name: /Les jeunes via l’application pass Culture/,
      })
    )
    await userEvent.click(
      screen.getByRole('checkbox', { name: /Les groupes scolaires via ADAGE/ })
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith(
        '/inscription/preparation/resultats'
      )
    })
  })

  it('should save target customer to localStorage on submit', async () => {
    renderSimulatorTarget()

    await userEvent.click(
      screen.getByRole('checkbox', {
        name: /Les jeunes via l’application pass Culture/,
      })
    )
    await userEvent.click(screen.getByRole('button', { name: 'Continuer' }))

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalled()
    })

    const stored = localStorageManager.getItem(
      LOCAL_STORAGE_KEY.SIMULATOR_TARGET_CUSTOMER
    )
    expect(JSON.parse(stored!)).toEqual(
      expect.objectContaining({ individual: true })
    )
  })

  it('should restore checkboxes state from localStorage', async () => {
    localStorageManager.setItem(
      LOCAL_STORAGE_KEY.SIMULATOR_TARGET_CUSTOMER,
      JSON.stringify({ individual: true, educational: false })
    )

    renderSimulatorTarget()

    await waitFor(() => {
      expect(
        screen.getByRole('checkbox', {
          name: /Les jeunes via l’application pass Culture/,
        })
      ).toBeChecked()
    })

    expect(
      screen.getByRole('checkbox', {
        name: /Les groupes scolaires via ADAGE/,
      })
    ).not.toBeChecked()
  })
})
