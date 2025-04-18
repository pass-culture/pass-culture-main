import * as Dialog from '@radix-ui/react-dialog'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'

import { api } from 'apiClient/api'
import { SubcategoryIdEnum } from 'apiClient/v1'
import { IndividualOfferContextProvider } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import * as useNotification from 'commons/hooks/useNotification'
import {
  getIndividualOfferFactory,
  subcategoryFactory,
} from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import {
  StocksCalendarForm,
  StocksCalendarFormProps,
} from './StocksCalendarForm'

vi.mock('apiClient/api', () => ({
  api: {
    getCategories: vi.fn(),
    bulkCreateEventStocks: vi.fn(),
  },
}))

function renderStocksCalendarForm(props: StocksCalendarFormProps) {
  return renderWithProviders(
    <IndividualOfferContextProvider>
      <Dialog.Root defaultOpen>
        <StocksCalendarForm {...props} />
      </Dialog.Root>
    </IndividualOfferContextProvider>
  )
}

describe('StocksCalendarForm', () => {
  const notifyError = vi.fn()
  const notifySuccess = vi.fn()

  beforeEach(async () => {
    const notifsImport = (await vi.importActual(
      'commons/hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: notifyError,
      success: notifySuccess,
    }))

    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [],
      subcategories: [
        subcategoryFactory({
          id: SubcategoryIdEnum.SALON,
          canHaveOpeningHours: true,
        }),
      ],
    })
  })

  it('should sumbit the form when clicking on "Valider" and close the dialog', async () => {
    const afterValidate = vi.fn()
    const bulkCreateEventStocksSpy = vi
      .spyOn(api, 'bulkCreateEventStocks')
      .mockResolvedValueOnce({ stocks_count: 0 })

    renderStocksCalendarForm({
      offer: getIndividualOfferFactory({
        priceCategories: [{ id: 1, price: 10, label: 'Price category' }],
        subcategoryId: SubcategoryIdEnum.SALON,
      }),
      onAfterValidate: afterValidate,
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.type(
      screen.getByLabelText('Date *'),
      addDays(new Date(), 1).toISOString().split('T')[0]
    )

    await userEvent.type(screen.getByLabelText('Horaire 1 *'), '11:11')

    await userEvent.selectOptions(screen.getByLabelText('Tarif *'), '1')

    await userEvent.click(screen.getByRole('button', { name: 'Valider' }))

    expect(bulkCreateEventStocksSpy).toHaveBeenCalled()
    expect(notifySuccess).toHaveBeenCalled()
    expect(afterValidate).toHaveBeenCalled()
  })

  it('should sumbit the form whith multiple dates when clicking on "Valider"', async () => {
    const afterValidate = vi.fn()
    const bulkCreateEventStocksSpy = vi
      .spyOn(api, 'bulkCreateEventStocks')
      .mockResolvedValueOnce({ stocks_count: 0 })

    renderStocksCalendarForm({
      offer: getIndividualOfferFactory({
        priceCategories: [{ id: 1, price: 10, label: 'Price category' }],
        subcategoryId: SubcategoryIdEnum.SALON,
      }),
      onAfterValidate: afterValidate,
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.click(screen.getByLabelText(/Plusieurs jours, semaines/))

    await userEvent.type(
      screen.getByLabelText('Date de début *'),
      addDays(new Date(), 1).toISOString().split('T')[0]
    )

    await userEvent.type(
      screen.getByLabelText('Date de fin *'),
      addDays(new Date(), 3).toISOString().split('T')[0]
    )

    await userEvent.type(screen.getByLabelText('Horaire 1 *'), '11:11')

    await userEvent.selectOptions(screen.getByLabelText('Tarif *'), '1')

    await userEvent.click(screen.getByRole('button', { name: 'Valider' }))

    expect(bulkCreateEventStocksSpy).toHaveBeenCalled()
  })

  it('should show an error messages if the stocks cound not be created', async () => {
    const afterValidate = vi.fn()
    const bulkCreateEventStocksSpy = vi
      .spyOn(api, 'bulkCreateEventStocks')
      .mockRejectedValueOnce(null)

    renderStocksCalendarForm({
      offer: getIndividualOfferFactory({
        priceCategories: [{ id: 1, price: 10, label: 'Price category' }],
        subcategoryId: SubcategoryIdEnum.SALON,
      }),
      onAfterValidate: afterValidate,
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.type(
      screen.getByLabelText('Date *'),
      addDays(new Date(), 1).toISOString().split('T')[0]
    )

    await userEvent.type(screen.getByLabelText('Horaire 1 *'), '11:11')

    await userEvent.selectOptions(screen.getByLabelText('Tarif *'), '1')

    await userEvent.click(screen.getByRole('button', { name: 'Valider' }))

    expect(bulkCreateEventStocksSpy).toHaveBeenCalled()
    expect(notifySuccess).not.toHaveBeenCalled()
    expect(notifyError).toHaveBeenCalled()
    expect(afterValidate).toHaveBeenCalled()
  })

  it('should not display the the one day form until a specific day has been chosen', async () => {
    renderStocksCalendarForm({
      offer: getIndividualOfferFactory({
        subcategoryId: SubcategoryIdEnum.SALON,
      }),
      onAfterValidate: () => {},
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(screen.queryByLabelText('Horaire 1 *')).not.toBeInTheDocument()

    await userEvent.type(
      screen.getByLabelText('Date *'),
      addDays(new Date(), 1).toISOString().split('T')[0]
    )

    expect(screen.getByLabelText('Horaire 1 *')).toBeInTheDocument()
  })

  it('should not display the the one day form if multiple the option days/weeks is chosen', async () => {
    renderStocksCalendarForm({
      offer: getIndividualOfferFactory({
        subcategoryId: SubcategoryIdEnum.SALON,
      }),
      onAfterValidate: () => {},
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(screen.getByLabelText('Date *')).toBeInTheDocument()

    await userEvent.click(screen.getByLabelText(/Plusieurs jours, semaines/))

    expect(screen.queryByLabelText('Date *')).not.toBeInTheDocument()
  })

  it('should set a default price category if there is only one available', async () => {
    renderStocksCalendarForm({
      offer: getIndividualOfferFactory({
        priceCategories: [{ id: 1, label: 'Only price category', price: 0 }],
        subcategoryId: SubcategoryIdEnum.SALON,
      }),
      onAfterValidate: () => {},
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.type(
      screen.getByLabelText('Date *'),
      addDays(new Date(), 1).toISOString().split('T')[0]
    )

    expect(screen.getByLabelText('Tarif *')).toHaveValue('1')
  })

  it('should not set a default price category if there are more than one available', async () => {
    renderStocksCalendarForm({
      offer: getIndividualOfferFactory({
        priceCategories: [
          { id: 1, label: 'First price category', price: 0 },
          { id: 2, label: 'Second price category', price: 0 },
        ],
        subcategoryId: SubcategoryIdEnum.SALON,
      }),
      onAfterValidate: () => {},
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    await userEvent.type(
      screen.getByLabelText('Date *'),
      addDays(new Date(), 1).toISOString().split('T')[0]
    )

    expect(screen.getByLabelText('Tarif *')).toHaveValue('')
  })
})
