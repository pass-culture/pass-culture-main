import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import type { Step } from 'components/Breadcrumb'
import { renderWithProviders } from 'utils/renderWithProviders'

import Breadcrumb, { BreadcrumbProps, BreadcrumbStyle } from '../Breadcrumb'

const renderBreadcrumb = (props: BreadcrumbProps) => {
  renderWithProviders(<Breadcrumb {...props} />)
}

const onClick = vi.fn()

describe('Breadcrumb', () => {
  let props: BreadcrumbProps
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
        hash: 'recapitulatif',
      },
      {
        id: '4',
        label: 'Confirmation',
      },
    ]
    props = {
      activeStep: '2',
      steps: steps,
      styleType: BreadcrumbStyle.TAB,
    }
  })

  describe('tab breadcrumb', () => {
    beforeEach(() => {
      props.styleType = BreadcrumbStyle.TAB
    })

    it('should render tab breadcrumb', async () => {
      renderBreadcrumb(props)

      expect(screen.getByTestId('bc-tab')).toBeInTheDocument()

      const listItems = await screen.findAllByRole('listitem')

      expect(listItems).toHaveLength(4)
      expect(listItems[0]).toHaveTextContent('Informations')
      expect(listItems[0].getElementsByClassName('separator')).toHaveLength(0)
      expect(listItems[1]).toHaveTextContent('Stocks & Prix')
      expect(listItems[1].getElementsByClassName('separator')).toHaveLength(0)
      expect(listItems[2]).toHaveTextContent('Récapitulatif')
      expect(listItems[2].getElementsByClassName('separator')).toHaveLength(0)
      expect(listItems[3]).toHaveTextContent('Confirmation')
      expect(listItems[3].getElementsByClassName('separator')).toHaveLength(0)
    })

    it('should render link or hash when needed', () => {
      renderBreadcrumb(props)

      const informationLink = screen.getByText('Informations').closest('a')
      expect(informationLink).toHaveAttribute('href', '/informations')

      const StockLink = screen.getByText('Stocks & Prix').closest('a')
      expect(StockLink).toHaveAttribute('href', '/stocks')

      const SummaryLink = screen.getByText('Récapitulatif').closest('a')
      expect(SummaryLink).toHaveAttribute('href', '#recapitulatif')

      const ConfirmationLink = screen.getByText('Confirmation').closest('a')
      expect(ConfirmationLink).toBeNull()
    })

    it('should have right active element when it has url', async () => {
      renderBreadcrumb(props)

      const listItems = await screen.findAllByRole('listitem')

      expect(listItems).toHaveLength(4)
      expect(listItems[0].classList.contains('active')).toBe(false)
      expect(listItems[1].classList.contains('active')).toBe(true)
      expect(listItems[2].classList.contains('active')).toBe(false)
      expect(listItems[3].classList.contains('active')).toBe(false)
    })

    it('should trigger onClick', async () => {
      renderBreadcrumb(props)

      const informationLink = screen.getByText('Informations').closest('a')

      informationLink && (await userEvent.click(informationLink))

      expect(onClick).toHaveBeenCalledTimes(1)
    })
  })

  describe('stepper breadcrumb', () => {
    it('should render stepper breadcrumb', () => {
      props.styleType = BreadcrumbStyle.STEPPER

      renderBreadcrumb(props)

      expect(screen.getByTestId('stepper')).toBeInTheDocument()
      // see other tests in Stepper tests
    })
  })
})
