import { render, screen } from '@testing-library/react'
import { axe } from 'vitest-axe'

import { BubbleStepper } from './BubbleStepper'

describe('<BubbleStepper />', () => {
  it('should expose the current step and progress to assistive technologies', () => {
    render(<BubbleStepper page={2} total={4} />)

    const progress = screen.getByRole('list', {
      name: 'Progression du parcours',
    })
    const steps = screen.getAllByRole('listitem')

    expect(steps).toHaveLength(4)
    expect(steps[0]).toHaveTextContent('Étape 1 sur 4, terminée')
    expect(steps[1]).toHaveAttribute('aria-current', 'step')
    expect(steps[1]).toHaveTextContent('Étape 2 sur 4, active')
    expect(steps[3]).toHaveTextContent('Étape 4 sur 4, à venir')
    expect(progress.querySelectorAll('[aria-hidden="true"]')).toHaveLength(4)
  })

  it('should not take focus away from navigation controls when the step changes', () => {
    const { rerender } = render(
      <>
        <button type="button">Continuer</button>
        <BubbleStepper page={1} total={4} />
      </>
    )
    const continueButton = screen.getByRole('button', { name: 'Continuer' })
    continueButton.focus()

    rerender(
      <>
        <button type="button">Continuer</button>
        <BubbleStepper page={2} total={4} />
      </>
    )

    expect(continueButton).toHaveFocus()
  })

  it('should not make progress bubbles interactive', () => {
    render(<BubbleStepper page={1} total={4} />)

    expect(screen.queryByRole('button')).not.toBeInTheDocument()
    expect(screen.queryByRole('link')).not.toBeInTheDocument()
  })

  it('should render without accessibility violations', async () => {
    const { container } = render(<BubbleStepper page={1} total={4} />)

    expect(await axe(container)).toHaveNoViolations()
  })
})
