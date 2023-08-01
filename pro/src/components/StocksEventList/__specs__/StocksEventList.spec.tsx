import { screen, within } from '@testing-library/react'
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
  STOCKS_PER_PAGE,
  StocksEventListProps,
} from '../StocksEventList'

const mockLogEvent = vi.fn()

const mockSetSotcks = vi.fn()

const renderStocksEventList = (props: Partial<StocksEventListProps>) => {
  renderWithProviders(
    <StocksEventList
      stocks={props.stocks ?? []}
      priceCategories={[
        priceCategoryFactory({ label: 'Label', price: 12.5, id: 1 }),
        priceCategoryFactory({ label: 'Label', price: 5.5, id: 2 }),
        priceCategoryFactory({ label: 'Label', price: 30.5, id: 3 }),
      ]}
      departmentCode="78"
      setStocks={mockSetSotcks}
      offerId={1}
    />
  )
}

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
    expect(screen.getByLabelText('Filtrer par date')).toBeInTheDocument()
    expect(screen.getByLabelText('Filtrer par horaire')).toBeInTheDocument()
    expect(screen.getByText('18')).toBeInTheDocument()
    expect(
      screen.getByText('12,5 € - Label', { selector: 'td' })
    ).toBeInTheDocument()
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

  it('should sort stocks', async () => {
    renderStocksEventList({
      stocks: [
        individualStockEventListFactory({
          beginningDatetime: new Date('2021-10-13T12:00:00Z').toISOString(),
          priceCategoryId: 1,
        }),
        individualStockEventListFactory({
          beginningDatetime: new Date('2021-10-14T12:00:00Z').toISOString(),
          priceCategoryId: 2,
        }),
        individualStockEventListFactory({
          beginningDatetime: new Date('2021-10-15T12:00:00Z').toISOString(),
          priceCategoryId: 3,
        }),
      ],
    })

    expect(screen.getAllByRole('row')).toHaveLength(4) // 1 header + 3 rows
    expect(
      screen.queryAllByRole('img', { name: 'Trier par ordre croissant' })
    ).toHaveLength(
      5 // Number of sortable columns
    )
    within(screen.getAllByRole('row')[1]).getByText('12,5 € - Label')
    within(screen.getAllByRole('row')[2]).getByText('5,5 € - Label')
    within(screen.getAllByRole('row')[3]).getByText('30,5 € - Label')

    await userEvent.click(
      screen.getAllByRole('img', { name: 'Trier par ordre croissant' })[2]
    )
    within(screen.getAllByRole('row')[1]).getByText('5,5 € - Label')
    within(screen.getAllByRole('row')[2]).getByText('12,5 € - Label')
    within(screen.getAllByRole('row')[3]).getByText('30,5 € - Label')

    await userEvent.click(
      screen.getByRole('img', { name: 'Trier par ordre décroissant' })
    )
    within(screen.getAllByRole('row')[1]).getByText('30,5 € - Label')
    within(screen.getAllByRole('row')[2]).getByText('12,5 € - Label')
    within(screen.getAllByRole('row')[3]).getByText('5,5 € - Label')

    await userEvent.click(screen.getByRole('img', { name: 'Ne plus trier' }))
    within(screen.getAllByRole('row')[1]).getByText('12,5 € - Label')
    within(screen.getAllByRole('row')[2]).getByText('5,5 € - Label')
    within(screen.getAllByRole('row')[3]).getByText('30,5 € - Label')
  })

  it('should filter stocks', async () => {
    const filteredPriceCategoryId = 3

    renderStocksEventList({
      stocks: [
        individualStockEventListFactory({
          beginningDatetime: new Date('2021-10-15T12:00:00Z').toISOString(),
          priceCategoryId: 1,
        }),
        individualStockEventListFactory({
          beginningDatetime: new Date('2021-10-14T13:00:00Z').toISOString(),
          priceCategoryId: 2,
        }),
        individualStockEventListFactory({
          beginningDatetime: new Date('2021-10-14T12:00:00Z').toISOString(),
          priceCategoryId: filteredPriceCategoryId,
        }),
      ],
    })

    expect(screen.getAllByRole('row')).toHaveLength(4) // 1 header + 3 stock rows

    await userEvent.type(
      screen.getByLabelText('Filtrer par date'),
      '2021-10-14'
    )
    expect(
      screen.getByText('Résultat de recherche', { exact: false })
    ).toBeInTheDocument()
    expect(screen.getAllByRole('row')).toHaveLength(4) // 1 header + 1 filter result row + 2 stock rows

    await userEvent.type(screen.getByLabelText('Filtrer par horaire'), '12:00')
    expect(screen.getAllByRole('row')).toHaveLength(3) // 1 header + 1 filter result row + 1 stock rows

    await userEvent.selectOptions(
      screen.getByLabelText('Filtrer par tarif'),
      String(filteredPriceCategoryId)
    )
    expect(screen.getAllByRole('row')).toHaveLength(3) // 1 header + 1 filter result row + 1 stock rows
  })

  it('should clear filters', async () => {
    const filteredPriceCategoryId = 3

    renderStocksEventList({
      stocks: [
        individualStockEventListFactory({
          beginningDatetime: new Date('2021-10-15T12:00:00Z').toISOString(),
          priceCategoryId: 1,
        }),
        individualStockEventListFactory({
          beginningDatetime: new Date('2021-10-14T13:00:00Z').toISOString(),
          priceCategoryId: 2,
        }),
        individualStockEventListFactory({
          beginningDatetime: new Date('2021-10-14T12:00:00Z').toISOString(),
          priceCategoryId: filteredPriceCategoryId,
        }),
      ],
    })

    await userEvent.type(
      screen.getByLabelText('Filtrer par date'),
      '2021-10-14'
    )
    expect(screen.getByText('Réinitialiser les filtres')).toBeInTheDocument()

    await userEvent.click(screen.getByText('Réinitialiser les filtres'))
    expect(
      screen.queryByText('Réinitialiser les filtres')
    ).not.toBeInTheDocument()
    expect(screen.getByLabelText('Filtrer par date')).toHaveValue('')
  })

  it('should change checkbox states', async () => {
    renderStocksEventList({
      stocks: [
        individualStockEventListFactory({ priceCategoryId: 1 }),
        individualStockEventListFactory({ priceCategoryId: 1 }),
      ],
    })
    const selectAllCheckbox = screen.getByLabelText('Tout sélectionner')
    const allCheckboxes = screen.getAllByRole('checkbox')

    // "all checkbox" check everithing
    await userEvent.click(selectAllCheckbox)
    expect(selectAllCheckbox).toBeChecked()
    expect(allCheckboxes[1]).toBeChecked()
    expect(allCheckboxes[2]).toBeChecked()

    // line checkbox partial check "all checkbox"
    await userEvent.click(allCheckboxes[1])
    expect(selectAllCheckbox).toBeChecked()
    expect(allCheckboxes[1]).not.toBeChecked()
    expect(allCheckboxes[2]).toBeChecked()

    // line checkbox check "all checkbox"
    await userEvent.click(allCheckboxes[1])
    expect(selectAllCheckbox).toBeChecked()
    expect(allCheckboxes[1]).toBeChecked()
    expect(allCheckboxes[2]).toBeChecked()

    // "all checkbox" uncheck everything
    await userEvent.click(selectAllCheckbox)
    expect(selectAllCheckbox).not.toBeChecked()
    expect(allCheckboxes[1]).not.toBeChecked()
    expect(allCheckboxes[2]).not.toBeChecked()
  })

  it('should check only filtered lines', async () => {
    renderStocksEventList({
      stocks: [
        individualStockEventListFactory({
          beginningDatetime: new Date('2021-10-15T12:00:00Z').toISOString(),
          priceCategoryId: 1,
        }),
        individualStockEventListFactory({
          beginningDatetime: new Date('2021-10-14T13:00:00Z').toISOString(),
          priceCategoryId: 2,
        }),
        individualStockEventListFactory({
          beginningDatetime: new Date('2021-10-14T12:00:00Z').toISOString(),
          priceCategoryId: 3,
        }),
      ],
    })

    expect(screen.getAllByRole('row')).toHaveLength(4) // 1 header + 3 stock rows

    await userEvent.selectOptions(
      screen.getByLabelText('Filtrer par tarif'),
      String(3)
    )
    expect(screen.getAllByRole('row')).toHaveLength(3) // 1 header + 1 filter result row + 1 stock rows

    await userEvent.click(screen.getByLabelText('Tout sélectionner'))
    expect(screen.getByText('1 date sélectionnée')).toBeInTheDocument()

    await userEvent.selectOptions(
      screen.getByLabelText('Filtrer par tarif'),
      ''
    )
    expect(
      screen.queryByText('date sélectionnée', { exact: false })
    ).not.toBeInTheDocument()
  })

  it('should bulk delete lines when clicking on button on action bar', async () => {
    renderStocksEventList({
      stocks: [
        individualStockEventListFactory({ priceCategoryId: 1 }),
        individualStockEventListFactory({ priceCategoryId: 1 }),
      ],
    })
    expect(
      screen.getAllByText('12,5 € - Label', { selector: 'td' })
    ).toHaveLength(2)

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
        offerId: 1,
        used: 'StockEventBulkDelete',
        to: 'stocks',
      }
    )
  })

  // test added because pagination has created a bug
  // where the last page was not changed when needed
  // user could have been to an empty page
  it('should bring me on new last page when deleting more than one page by action bar', async () => {
    const stocks = []
    for (let i = 0; i < STOCKS_PER_PAGE * 2 + 1; i++) {
      const stock = individualStockEventListFactory({ priceCategoryId: 1 })
      stocks.push(stock)
    }

    renderStocksEventList({
      stocks: stocks,
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
    await userEvent.click(screen.getByRole('button', { name: 'Page suivante' }))
    expect(screen.getByText('Page 2/3')).toBeInTheDocument()
    const secondPageCheckboxes = screen.getAllByRole('checkbox')
    await userEvent.click(secondPageCheckboxes[1])
    expect(
      screen.getByText(`${STOCKS_PER_PAGE} dates sélectionnées`)
    ).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'Page suivante' }))
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
        uuid: expect.any(String),
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
    expect(
      screen.getAllByText('12,5 € - Label', { selector: 'td' })
    ).toHaveLength(2)

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
        uuid: expect.any(String),
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
        offerId: 1,
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
    await userEvent.click(screen.getByRole('button', { name: 'Page suivante' }))
    await userEvent.click(screen.getByRole('button', { name: 'Page suivante' }))
    expect(screen.getByText('Page 3/3')).toBeInTheDocument()
    // delete by trash icon
    await userEvent.click(screen.getAllByText('Supprimer')[0])

    // only one line has been removed, last page is full
    expect(screen.getByText('Page 2/2')).toBeInTheDocument()
    expect(
      screen.getAllByText('12,5 € - Label', { selector: 'td' })
    ).toHaveLength(STOCKS_PER_PAGE)
  })
})
