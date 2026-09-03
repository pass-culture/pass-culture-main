import { act, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { vi } from 'vitest'
import { axe } from 'vitest-axe'

import type { StepItem } from './Stepper'
import { STEPPER_MIN_WIDTH_PER_STEP, Stepper } from './Stepper'

describe('Stepper', () => {
  const defaultSteps: StepItem[] = [
    {
      id: 'category',
      label: 'Choisissez votre catégorie',
      url: '/category',
      onClick: vi.fn(),
    },
    {
      id: 'pricing',
      label: 'Définissez un tarif',
      url: '/pricing',
      onClick: vi.fn(),
    },
    {
      id: 'validation',
      label: 'Validez votre offre',
      url: '/validation',
      onClick: vi.fn(),
    },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should render without accessibility violations', async () => {
    const { container } = render(
      <MemoryRouter>
        <Stepper steps={defaultSteps} activeStep="pricing" />
      </MemoryRouter>
    )
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should render all steps with correct numbers', () => {
    render(
      <MemoryRouter>
        <Stepper steps={defaultSteps} activeStep="pricing" />
      </MemoryRouter>
    )

    expect(screen.getByText('1')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()

    expect(screen.getByText('Choisissez votre catégorie')).toBeInTheDocument()
    expect(screen.getByText('Définissez un tarif')).toBeInTheDocument()
    expect(screen.getByText('Validez votre offre')).toBeInTheDocument()
  })

  it('should format VoiceOver text correctly for screen readers', () => {
    render(
      <MemoryRouter>
        <Stepper steps={defaultSteps} activeStep="pricing" />
      </MemoryRouter>
    )

    // Step 1: index 0 < activeStepIndex 1 => Done (terminée)
    // Step 2: index 1 === activeStepIndex 1 => Current (active)
    // Step 3: index 2 > activeStepIndex 1 => Disabled (à venir)

    expect(
      screen.getByLabelText(
        'Étape 1 sur 3, terminée, Choisissez votre catégorie'
      )
    ).toBeInTheDocument()
    expect(
      screen.getAllByText('Étape 2 sur 3, active, Définissez un tarif').length
    ).toBeGreaterThan(0)
    // Disabled steps are visually hidden for screen readers inside a static span
    expect(
      screen.getByText('Étape 3 sur 3, à venir, Validez votre offre')
    ).toBeInTheDocument()
  })

  it('should flag the current step with aria-current', () => {
    render(
      <MemoryRouter>
        <Stepper steps={defaultSteps} activeStep="pricing" />
      </MemoryRouter>
    )

    const [category, pricing, validation] = screen.getAllByRole('listitem')

    expect(category).not.toHaveAttribute('aria-current')
    expect(pricing).toHaveAttribute('aria-current', 'step')
    expect(validation).not.toHaveAttribute('aria-current')
  })

  it('should render a Link only for completed steps that have a url', () => {
    render(
      <MemoryRouter>
        <Stepper steps={defaultSteps} activeStep="pricing" />
      </MemoryRouter>
    )

    // Step 1 (done with url) is the only navigable step
    const step1Link = screen
      .getByText('Choisissez votre catégorie')
      .closest('a')
    expect(step1Link).toHaveAttribute('href', '/category')

    // Step 2 is the current step: linking to the page already displayed
    expect(screen.getByText('Définissez un tarif').closest('a')).toBeNull()

    // Step 3 is not reachable yet
    expect(screen.getByText('Validez votre offre').closest('a')).toBeNull()
  })

  it('should render button when step has onClick but no url', () => {
    const stepsWithoutUrl: StepItem[] = [
      { id: 'step1', label: 'Step with onClick only', onClick: vi.fn() },
      { id: 'step2', label: 'Step two', onClick: vi.fn() },
      { id: 'step3', label: 'Step three' },
    ]
    render(
      <MemoryRouter>
        <Stepper steps={stepsWithoutUrl} activeStep="step2" />
      </MemoryRouter>
    )

    expect(
      screen.getByRole('button', {
        name: 'Étape 1 sur 3, terminée, Step with onClick only',
      })
    ).toBeInTheDocument()
    // The current step is not actionable
    expect(screen.getAllByRole('button')).toHaveLength(1)
  })

  it('should handle click on Link steps and trigger onClick callback', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <Stepper steps={defaultSteps} activeStep="pricing" />
      </MemoryRouter>
    )

    const step1Link = screen.getByLabelText(
      'Étape 1 sur 3, terminée, Choisissez votre catégorie'
    )

    await user.click(step1Link)
    expect(defaultSteps[0].onClick).toHaveBeenCalledTimes(1)
  })

  it('should render every step as upcoming when activeStep matches no step', () => {
    render(
      <MemoryRouter>
        <Stepper steps={defaultSteps} activeStep="unknown-step" />
      </MemoryRouter>
    )

    expect(screen.queryAllByRole('link')).toHaveLength(0)
    expect(
      screen.getByText('Étape 1 sur 3, à venir, Choisissez votre catégorie')
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('listitem', { current: 'step' })
    ).not.toBeInTheDocument()
  })

  it('should force orientation layout when orientation prop is provided', () => {
    const { container: containerHoriz } = render(
      <MemoryRouter>
        <Stepper
          steps={defaultSteps}
          activeStep="pricing"
          orientation="horizontal"
        />
      </MemoryRouter>
    )
    expect(containerHoriz.querySelector('.horizontal')).toBeInTheDocument()
    expect(containerHoriz.querySelector('.vertical')).not.toBeInTheDocument()

    const { container: containerVert } = render(
      <MemoryRouter>
        <Stepper
          steps={defaultSteps}
          activeStep="pricing"
          orientation="vertical"
        />
      </MemoryRouter>
    )
    expect(containerVert.querySelector('.vertical')).toBeInTheDocument()
    expect(containerVert.querySelector('.horizontal')).not.toBeInTheDocument()
  })

  it('should dynamically switch to vertical layout when width is below threshold (STEPPER_MIN_WIDTH_PER_STEP per step)', () => {
    let resizeCallback: any = null
    const mockObserve = vi.fn()
    const mockDisconnect = vi.fn()

    class MockResizeObserver {
      constructor(callback: any) {
        resizeCallback = callback
      }
      observe = mockObserve
      disconnect = mockDisconnect
    }

    vi.stubGlobal('ResizeObserver', MockResizeObserver)

    const { container } = render(
      <MemoryRouter>
        <Stepper steps={defaultSteps} activeStep="pricing" orientation="auto" />
      </MemoryRouter>
    )

    expect(mockObserve).toHaveBeenCalled()

    const STEPPER_MIN_WIDTH = STEPPER_MIN_WIDTH_PER_STEP * defaultSteps.length

    // Trigger width change to be greater than STEPPER_MIN_WIDTH -> should switch to horizontal
    act(() => {
      resizeCallback([
        {
          contentRect: {
            width: STEPPER_MIN_WIDTH + 100,
          },
        },
      ])
    })
    expect(container.querySelector('.horizontal')).toBeInTheDocument()
    expect(container.querySelector('.vertical')).not.toBeInTheDocument()

    // Trigger width change to be less than STEPPER_MIN_WIDTH -> should switch to vertical
    act(() => {
      resizeCallback([
        {
          contentRect: {
            width: STEPPER_MIN_WIDTH - 100,
          },
        },
      ])
    })
    expect(container.querySelector('.vertical')).toBeInTheDocument()
    expect(container.querySelector('.horizontal')).not.toBeInTheDocument()

    vi.unstubAllGlobals()
  })
})
