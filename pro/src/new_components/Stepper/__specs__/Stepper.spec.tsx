import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { MemoryRouter } from 'react-router-dom'

import type { Step } from 'new_components/Breadcrumb'

import Stepper, { IStepper } from '../Stepper'

const renderStepper = (props: IStepper) => {
  return render(
    <MemoryRouter>
      <Stepper {...props} />
    </MemoryRouter>
  )
}

const onClick = jest.fn()

describe('Stepper', () => {
  let props: IStepper
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
      },
    ]
    props = {
      activeStep: '2',
      steps: steps,
    }
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

  it('should render link when needed', async () => {
    renderStepper(props)

    const informationLink = await screen.getByText('Informations').closest('a')
    expect(informationLink).toHaveAttribute('href', '/informations')

    const StockLink = await screen.getByText('Stocks & Prix').closest('a')
    expect(StockLink).toHaveAttribute('href', '/stocks')

    const SummaryLink = await screen.getByText('Récapitulatif').closest('a')
    expect(SummaryLink).toHaveAttribute('href', '/recapitulatif')

    const ConfirmationLink = await screen.getByText('Confirmation').closest('a')
    expect(ConfirmationLink).toBeNull()
  })

  it('should have right active element and be seelctionnable when it has url', async () => {
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

    const informationLink = await screen.getByText('Informations').closest('a')

    informationLink && (await userEvent.click(informationLink))

    expect(onClick).toHaveBeenCalledTimes(1)
  })
})
