import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { type Step, Stepper, type StepperProps } from '../Stepper'

const renderStepper = (props: StepperProps) => {
  return renderWithProviders(<Stepper {...props} />)
}

const onClick = vi.fn()

describe('Stepper', () => {
  let props: StepperProps
  let steps: Step[]

  beforeEach(() => {
    steps = [
      {
        id: '1',
        label: 'Informations',
        url: '/informations',
        onClick: onClick,
      },
      {
        id: '2',
        label: 'Stocks & Prix',
        url: '/stocks',
      },
      {
        id: '3',
        label: 'Récapitulatif',
        url: '/recapitulatif',
      },
      {
        id: '4',
        label: 'Confirmation',
        disabled: true,
      },
    ]
    props = {
      activeStep: '2',
      steps: steps,
    }
  })

  it('should check content for accessibility', async () => {
    const { container } = renderStepper(props)

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display stepper with number and label', async () => {
    renderStepper(props)

    const listItems = await screen.findAllByRole('listitem')

    expect(listItems).toHaveLength(4)
    expect(listItems[0]).toHaveTextContent('1')
    expect(listItems[0]).toHaveTextContent('Informations')
    expect(listItems[1]).toHaveTextContent('2')
    expect(listItems[1]).toHaveTextContent('Stocks & Prix')
    expect(listItems[2]).toHaveTextContent('3')
    expect(listItems[2]).toHaveTextContent('Récapitulatif')
    expect(listItems[3]).toHaveTextContent('4')
    expect(listItems[3]).toHaveTextContent('Confirmation')
  })

  it('should render link when needed', () => {
    renderStepper(props)

    const informationLink = screen.getByText('Informations').closest('a')
    expect(informationLink).toHaveAttribute('href', '/informations')

    const StockLink = screen.getByText('Stocks & Prix').closest('a')
    expect(StockLink).toHaveAttribute('href', '/stocks')

    const SummaryLink = screen.getByText('Récapitulatif').closest('a')
    expect(SummaryLink).toHaveAttribute('href', '/recapitulatif')

    const ConfirmationLink = screen.getByText('Confirmation').closest('a')
    expect(ConfirmationLink).toBeNull()
  })

  it('should not render link when step has url but is disabled', () => {
    const stepsWithDisabledUrl: Step[] = [
      { id: '1', label: 'Informations', url: '/informations' },
      { id: '2', label: 'Stocks & Prix', url: '/stocks', disabled: true },
    ]
    renderStepper({ activeStep: '1', steps: stepsWithDisabledUrl })

    const disabledLink = screen.getByText('Stocks & Prix').closest('a')
    expect(disabledLink).toBeNull()
  })

  it('should be selectionnable without a url when not disabled', async () => {
    const stepsWithoutUrl: Step[] = [
      { id: '1', label: 'Done step' },
      { id: '2', label: 'Disabled step', disabled: true },
    ]
    renderStepper({ activeStep: '1', steps: stepsWithoutUrl })

    const listItems = await screen.findAllByRole('listitem')
    expect(listItems[0].classList.contains('selectionnable')).toBe(true)
    expect(listItems[1].classList.contains('selectionnable')).toBe(false)
  })

  it('should have right active element and be selectionnable when not disabled', async () => {
    renderStepper(props)

    const listItems = await screen.findAllByRole('listitem')

    expect(listItems).toHaveLength(4)
    expect(listItems[0].classList.contains('selectionnable')).toBe(true)
    expect(listItems[0].classList.contains('active')).toBe(false)
    expect(listItems[1].classList.contains('selectionnable')).toBe(true)
    expect(listItems[1].classList.contains('active')).toBe(true)
    expect(listItems[2].classList.contains('selectionnable')).toBe(true)
    expect(listItems[2].classList.contains('active')).toBe(false)
    expect(listItems[3].classList.contains('selectionnable')).toBe(false)
    expect(listItems[3].classList.contains('active')).toBe(false)
  })

  it('should trigger onClick', async () => {
    renderStepper(props)

    const informationLink = screen.getByText('Informations').closest('a')

    if (informationLink) {
      await userEvent.click(informationLink)
    }

    expect(onClick).toHaveBeenCalledTimes(1)
  })
})
