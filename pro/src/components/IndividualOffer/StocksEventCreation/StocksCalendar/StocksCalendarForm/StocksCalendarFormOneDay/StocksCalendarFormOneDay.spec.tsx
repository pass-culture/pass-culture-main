import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'
import { FormProvider, useForm } from 'react-hook-form'

import { api } from 'apiClient/api'
import { SubcategoryIdEnum } from 'apiClient/v1'
import { IndividualOfferContextProvider } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  subcategoryFactory,
} from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import {
  DurationTypeOption,
  StocksCalendarFormValues,
  TimeSlotTypeOption,
} from 'components/IndividualOffer/StocksEventCreation/form/types'

import { StocksCalendarFormOneDay } from './StocksCalendarFormOneDay'

vi.mock('apiClient/api', () => ({
  api: {
    getCategories: vi.fn(),
  },
}))

function renderStocksCalendarFormOneDay(
  defaultOptions?: Partial<StocksCalendarFormValues>
) {
  function StocksCalendarFormOneDayWrapper() {
    const form = useForm<StocksCalendarFormValues>({
      defaultValues: {
        durationType: DurationTypeOption.ONE_DAY,
        timeSlotType: TimeSlotTypeOption.SPECIFIC_TIME,
        specificTimeSlots: [{ slot: '' }],
        pricingCategoriesQuantities: [{ priceCategory: '' }],
        oneDayDate: '',
        ...defaultOptions,
      },
    })

    return (
      <IndividualOfferContextProvider>
        <FormProvider {...form}>
          <StocksCalendarFormOneDay
            form={form}
            offer={getIndividualOfferFactory({
              subcategoryId: SubcategoryIdEnum.SALON,
            })}
          />
        </FormProvider>
      </IndividualOfferContextProvider>
    )
  }

  return renderWithProviders(<StocksCalendarFormOneDayWrapper />)
}

describe('StocksCalendarFormOneDay', () => {
  beforeEach(() => {
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

  it('should show the time slots form when the specific time option is chosen', async () => {
    renderStocksCalendarFormOneDay({
      oneDayDate: addDays(new Date(), 1).toISOString().split('T')[0],
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.getByRole('button', { name: 'Ajouter un horaire' })
    ).toBeInTheDocument()

    await userEvent.click(screen.getByLabelText(/Aux horaires d’ouverture/))

    expect(
      screen.queryByRole('button', { name: 'Ajouter un horaire' })
    ).not.toBeInTheDocument()
  })

  it('should not display the form if the date is invalid', async () => {
    renderStocksCalendarFormOneDay()

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.queryByRole('heading', { name: 'Le public doit se présenter :' })
    ).not.toBeInTheDocument()

    await userEvent.type(
      screen.getByLabelText('Date *'),
      addDays(new Date(), 1).toISOString().split('T')[0]
    )

    expect(
      screen.getByRole('heading', { name: 'Le public doit se présenter :' })
    ).toBeInTheDocument()
  })
})
