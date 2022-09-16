import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { MemoryRouter } from 'react-router-dom'

import type { Step } from 'new_components/Breadcrumb'

import Breadcrumb, { BreadcrumbStyle, IBreadcrumb } from '../Breadcrumb'

const renderBreadcrumb = (props: IBreadcrumb) => {
  return render(
    <MemoryRouter>
      <Breadcrumb {...props} />
    </MemoryRouter>
  )
}

const onClick = jest.fn()

describe('Breadcrumb', () => {
  let props: IBreadcrumb
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
      styleType: BreadcrumbStyle.DEFAULT,
    }
  })

  describe('default breadcrumb', () => {
    beforeEach(() => {
      props.styleType = BreadcrumbStyle.DEFAULT
    })

    it('should render default breadcrumb', async () => {
      renderBreadcrumb(props)

      expect(await screen.getByTestId('bc-default')).toBeInTheDocument()

      const listItems = await screen.findAllByRole('listitem')

      expect(listItems).toHaveLength(4)
      expect(listItems[0]).toHaveTextContent('Informations')
      expect(
        await listItems[0].getElementsByClassName('separator')
      ).toHaveLength(1)
      expect(listItems[1]).toHaveTextContent('Stocks & Prix')
      expect(
        await listItems[1].getElementsByClassName('separator')
      ).toHaveLength(1)
      expect(listItems[2]).toHaveTextContent('Récapitulatif')
      expect(
        await listItems[2].getElementsByClassName('separator')
      ).toHaveLength(1)
      expect(listItems[3]).toHaveTextContent('Confirmation')
      expect(
        await listItems[3].getElementsByClassName('separator')
      ).toHaveLength(0)
    })

    it('should render link or hash when needed', async () => {
      renderBreadcrumb(props)

      const informationLink = await screen
        .getByText('Informations')
        .closest('a')
      expect(informationLink).toHaveAttribute('href', '/informations')

      const StockLink = await screen.getByText('Stocks & Prix').closest('a')
      expect(StockLink).toHaveAttribute('href', '/stocks')

      const SummaryLink = await screen.getByText('Récapitulatif').closest('a')
      expect(SummaryLink).toHaveAttribute('href', '#recapitulatif')

      const ConfirmationLink = await screen
        .getByText('Confirmation')
        .closest('a')
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

      const informationLink = await screen
        .getByText('Informations')
        .closest('a')

      informationLink && (await userEvent.click(informationLink))

      expect(onClick).toHaveBeenCalledTimes(1)
    })
  })

  describe('tab breadcrumb', () => {
    beforeEach(() => {
      props.styleType = BreadcrumbStyle.TAB
    })

    it('should render tab breadcrumb', async () => {
      renderBreadcrumb(props)

      expect(await screen.getByTestId('bc-tab')).toBeInTheDocument()

      const listItems = await screen.findAllByRole('listitem')

      expect(listItems).toHaveLength(4)
      expect(listItems[0]).toHaveTextContent('Informations')
      expect(
        await listItems[0].getElementsByClassName('separator')
      ).toHaveLength(0)
      expect(listItems[1]).toHaveTextContent('Stocks & Prix')
      expect(
        await listItems[1].getElementsByClassName('separator')
      ).toHaveLength(0)
      expect(listItems[2]).toHaveTextContent('Récapitulatif')
      expect(
        await listItems[2].getElementsByClassName('separator')
      ).toHaveLength(0)
      expect(listItems[3]).toHaveTextContent('Confirmation')
      expect(
        await listItems[3].getElementsByClassName('separator')
      ).toHaveLength(0)
    })

    it('should render link or hash when needed', async () => {
      renderBreadcrumb(props)

      const informationLink = await screen
        .getByText('Informations')
        .closest('a')
      expect(informationLink).toHaveAttribute('href', '/informations')

      const StockLink = await screen.getByText('Stocks & Prix').closest('a')
      expect(StockLink).toHaveAttribute('href', '/stocks')

      const SummaryLink = await screen.getByText('Récapitulatif').closest('a')
      expect(SummaryLink).toHaveAttribute('href', '#recapitulatif')

      const ConfirmationLink = await screen
        .getByText('Confirmation')
        .closest('a')
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

      const informationLink = await screen
        .getByText('Informations')
        .closest('a')

      informationLink && (await userEvent.click(informationLink))

      expect(onClick).toHaveBeenCalledTimes(1)
    })
  })

  describe('stepper breadcrumb', () => {
    it('should render stepper breadcrumb', async () => {
      props.styleType = BreadcrumbStyle.STEPPER

      renderBreadcrumb(props)

      expect(await screen.getByTestId('stepper')).toBeInTheDocument()
      // see other tests in Stepper tests
    })
  })
})
