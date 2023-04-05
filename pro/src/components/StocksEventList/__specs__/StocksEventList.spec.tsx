import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import {
  individualStockEventListFactory,
  priceCategoryFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import StocksEventList, {
  IStocksEvent,
  STOCKS_PER_PAGE,
} from '../StocksEventList'

const mockLogEvent = jest.fn()

const mockSetSotcks = jest.fn()
interface IrenderStocksEventList {
  stocks: IStocksEvent[]
}

const renderStocksEventList = ({ stocks }: IrenderStocksEventList) =>
  renderWithProviders(
    <StocksEventList
      stocks={stocks}
      priceCategories={[
        priceCategoryFactory({ label: 'Label', price: 12.38, id: 1 }),
      ]}
      departmentCode="78"
      setStocks={mockSetSotcks}
      offerId={'AA'}
    />
  )

describe('StocksEventList', () => {
  beforeEach(() => {
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should render a table with header and data', () => {
    renderStocksEventList({
      stocks: [individualStockEventListFactory({ priceCategoryId: 1 })],
    })

    expect(screen.getByText('Date')).toBeInTheDocument()

    expect(screen.getByText('ven')).toBeInTheDocument()
    expect(screen.getByText('15/10/2021')).toBeInTheDocument()
    expect(screen.getByText('14:00')).toBeInTheDocument()
    expect(screen.getByText('18')).toBeInTheDocument()
    expect(screen.getByText('12,38 € - Label')).toBeInTheDocument()
    expect(screen.getByText('15/09/2021')).toBeInTheDocument()
  })

  it('should render Illimité', () => {
    renderStocksEventList({
      stocks: [
        individualStockEventListFactory({ priceCategoryId: 1, quantity: null }),
      ],
    })

    expect(screen.getByText('Illimité')).toBeInTheDocument()
  })

  it('should manage checkboxes', async () => {
    renderStocksEventList({
      stocks: [
        individualStockEventListFactory({ priceCategoryId: 1 }),
        individualStockEventListFactory({ priceCategoryId: 1 }),
      ],
    })
    const checkboxes = screen.getAllByRole('checkbox')

    // "all checkbox" check everithing
    await userEvent.click(checkboxes[0])
    expect(checkboxes[0]).toBeChecked()
    expect(checkboxes[1]).toBeChecked()
    expect(checkboxes[2]).toBeChecked()

    // line checkbox uncheck "all checkbox"
    await userEvent.click(checkboxes[1])
    expect(checkboxes[0]).not.toBeChecked()
    expect(checkboxes[1]).not.toBeChecked()
    expect(checkboxes[2]).toBeChecked()

    // line checkbox check "all checkbox"
    await userEvent.click(checkboxes[1])
    expect(checkboxes[0]).toBeChecked()
    expect(checkboxes[1]).toBeChecked()
    expect(checkboxes[2]).toBeChecked()

    // "all checkbox" uncheck everithing
    await userEvent.click(checkboxes[0])
    expect(checkboxes[0]).not.toBeChecked()
    expect(checkboxes[1]).not.toBeChecked()
    expect(checkboxes[2]).not.toBeChecked()
  })

  it('should bulk delete lines when clicking on button on action bar', async () => {
    renderStocksEventList({
      stocks: [
        individualStockEventListFactory({ priceCategoryId: 1 }),
        individualStockEventListFactory({ priceCategoryId: 1 }),
      ],
    })
    expect(screen.getAllByText('12,38 € - Label')).toHaveLength(2)

    const checkboxes = screen.getAllByRole('checkbox')
    await userEvent.click(checkboxes[0])
    expect(screen.getByText('2 dates sélectionnées')).toBeInTheDocument()

    await userEvent.click(screen.getByText('Supprimer ces dates'))
    expect(mockSetSotcks).toBeCalledTimes(1)
    expect(mockSetSotcks).toHaveBeenNthCalledWith(1, [])

    expect(screen.queryByText('2 dates sélectionnées')).not.toBeInTheDocument()
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        deletionCount: '2',
        isDraft: false,
        isEdition: true,
        offerId: 'AA',
        used: 'StockEventBulkDelete',
        to: 'stocks',
      }
    )
  })

  // test added because pagination has created a bug
  // where the last page was not changed when needed
  // user could have been to an empty page
  it('should bring me on new last page when deleting more than one page by action bar', async () => {
    renderStocksEventList({
      stocks: Array(STOCKS_PER_PAGE * 2 + 1).fill(
        individualStockEventListFactory({ priceCategoryId: 1 })
      ),
    })

    // select all lines but not first page
    const firstPageCheckboxes = screen.getAllByRole('checkbox')
    for (let i = 0; i <= STOCKS_PER_PAGE; i++) {
      await userEvent.click(firstPageCheckboxes[i])
    }
    expect(
      screen.getByText(`${STOCKS_PER_PAGE + 1} dates sélectionnées`)
    ).toBeInTheDocument()

    // going page 2 ...and select one less line
    await userEvent.click(screen.getByAltText('Page suivante'))
    expect(screen.getByText('Page 2/3')).toBeInTheDocument()
    const secondPageCheckboxes = screen.getAllByRole('checkbox')
    await userEvent.click(secondPageCheckboxes[1])
    expect(
      screen.getByText(`${STOCKS_PER_PAGE} dates sélectionnées`)
    ).toBeInTheDocument()

    await userEvent.click(screen.getByAltText('Page suivante'))
    expect(screen.getByText('Page 3/3')).toBeInTheDocument()

    // delete by action bar
    await userEvent.click(screen.getByText('Supprimer ces dates'))
    expect(mockSetSotcks).toBeCalledTimes(1)
    expect(mockSetSotcks).toHaveBeenNthCalledWith(
      1,
      Array(STOCKS_PER_PAGE + 1).fill({
        beginningDatetime: '2021-10-15T12:00:00.000Z',
        bookingLimitDatetime: '2021-09-15T12:00:00.000Z',
        priceCategoryId: 1,
        quantity: 18,
      })
    )

    // we are on page 2 now (setStocks is mocked so lines are still here)
    expect(screen.getByText('Page 2/3')).toBeInTheDocument()
  })

  it('should delete line when clicking on trash icon', async () => {
    renderStocksEventList({
      stocks: [
        individualStockEventListFactory({ priceCategoryId: 1 }),
        individualStockEventListFactory({ priceCategoryId: 1 }),
      ],
    })
    expect(screen.getAllByText('12,38 € - Label')).toHaveLength(2)

    const checkboxes = screen.getAllByRole('checkbox')
    await userEvent.click(checkboxes[0])
    expect(screen.getByText('2 dates sélectionnées')).toBeInTheDocument()

    await userEvent.click(screen.getAllByText('Supprimer')[0])
    expect(screen.getByText('1 date sélectionnée')).toBeInTheDocument()
    expect(mockSetSotcks).toBeCalledTimes(1)
    expect(mockSetSotcks).toHaveBeenNthCalledWith(1, [
      {
        beginningDatetime: '2021-10-15T12:00:00.000Z',
        bookingLimitDatetime: '2021-09-15T12:00:00.000Z',
        priceCategoryId: 1,
        quantity: 18,
      },
    ])
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: false,
        isEdition: true,
        offerId: 'AA',
        used: 'StockEventDelete',
        to: 'stocks',
      }
    )
  })

  // test added because pagination has created a bug
  // where several lines where deleted at the same time
  // and the last page was not changed when needed
  it('should bring me on previous page when deleting only one line by trash icon', async () => {
    renderStocksEventList({
      stocks: Array(STOCKS_PER_PAGE * 2 + 1).fill(
        individualStockEventListFactory({ priceCategoryId: 1 })
      ),
    })

    // going page 3 (last page)
    await userEvent.click(screen.getByAltText('Page suivante'))
    await userEvent.click(screen.getByAltText('Page suivante'))
    expect(screen.getByText('Page 3/3')).toBeInTheDocument()
    // delete by trash icon
    await userEvent.click(screen.getAllByText('Supprimer')[0])

    // only one line has been removed, last page is full
    expect(screen.getByText('Page 2/2')).toBeInTheDocument()
    expect(screen.getAllByText('12,38 € - Label')).toHaveLength(STOCKS_PER_PAGE)
  })
})
