import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays } from 'date-fns'
import { FormProvider, useForm } from 'react-hook-form'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferWithAddressResponseModel,
  SubcategoryIdEnum,
} from 'apiClient/v1'
import { IndividualOfferContextProvider } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  subcategoryFactory,
} from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { weekDays } from 'components/IndividualOffer/StocksEventCreation/form/constants'
import {
  DurationTypeOption,
  StocksCalendarFormValues,
  TimeSlotTypeOption,
} from 'components/IndividualOffer/StocksEventCreation/form/types'

import { StocksCalendarFormMultipleDays } from './StocksCalendarFormMultipleDays'

vi.mock('apiClient/api', () => ({
  api: {
    getCategories: vi.fn(),
  },
}))

function renderStocksCalendarFormMultipleDays(
  defaultFormValues: Partial<StocksCalendarFormValues> = {},
  offer: GetIndividualOfferWithAddressResponseModel = getIndividualOfferFactory(
    {
      subcategoryId: SubcategoryIdEnum.SALON,
    }
  )
) {
  function StocksCalendarFormMultipleDaysWrapper() {
    const form = useForm<StocksCalendarFormValues>({
      defaultValues: {
        durationType: DurationTypeOption.MULTIPLE_DAYS_WEEKS,
        timeSlotType: TimeSlotTypeOption.SPECIFIC_TIME,
        specificTimeSlots: [{ slot: '' }],
        pricingCategoriesQuantities: [{ priceCategory: '' }],
        oneDayDate: '',
        multipleDaysWeekDays: weekDays.map((d) => ({
          label: d.label,
          value: d.value,
          checked: true,
        })),
        ...defaultFormValues,
      },
    })

    return (
      <IndividualOfferContextProvider>
        <FormProvider {...form}>
          <StocksCalendarFormMultipleDays form={form} offer={offer} />
        </FormProvider>
      </IndividualOfferContextProvider>
    )
  }

  return renderWithProviders(<StocksCalendarFormMultipleDaysWrapper />)
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
    renderStocksCalendarFormMultipleDays({
      multipleDaysStartDate: addDays(new Date(), 1).toISOString().split('T')[0],
      multipleDaysEndDate: addDays(new Date(), 3).toISOString().split('T')[0],
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

  it('should not display the week day form if the end date is empty, unless the "no end date" checkbox is checked', async () => {
    renderStocksCalendarFormMultipleDays({
      multipleDaysStartDate: addDays(new Date(), 1).toISOString().split('T')[0],
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.queryByText('Sélectionnez les jours : *')
    ).not.toBeInTheDocument()

    await userEvent.type(
      screen.getByLabelText('Date de fin *'),
      addDays(new Date(), 3).toISOString().split('T')[0]
    )

    expect(screen.getByText('Sélectionnez les jours : *')).toBeInTheDocument()

    await userEvent.clear(screen.getByLabelText('Date de fin *'))

    expect(
      screen.queryByText('Sélectionnez les jours : *')
    ).not.toBeInTheDocument()

    await userEvent.click(screen.getByLabelText('Pas de date de fin'))

    expect(screen.getByText('Sélectionnez les jours : *')).toBeInTheDocument()
  })

  it('should not display the time form if no weekday is selected', async () => {
    renderStocksCalendarFormMultipleDays({
      multipleDaysStartDate: addDays(new Date(), 1).toISOString().split('T')[0],
      multipleDaysHasNoEndDate: true,
      multipleDaysWeekDays: weekDays.map((d) => ({
        label: d.label,
        value: d.value,
        checked: false,
      })),
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(screen.getByText('Sélectionnez les jours : *')).toBeInTheDocument()

    expect(
      screen.queryByRole('heading', { name: 'Le public doit se présenter :' })
    ).not.toBeInTheDocument()

    await userEvent.click(screen.getByLabelText('Lundi'))

    expect(
      screen.getByRole('heading', { name: 'Le public doit se présenter :' })
    ).toBeInTheDocument()
  })

  it('should have all week days initially selected when the checkbox "no end date" is checked', async () => {
    renderStocksCalendarFormMultipleDays({
      multipleDaysStartDate: addDays(new Date(), 1).toISOString().split('T')[0],
      multipleDaysHasNoEndDate: true,
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(screen.queryByLabelText('Lundi')).toBeChecked()
    expect(screen.getByLabelText('Mardi')).toBeChecked()
    expect(screen.getByLabelText('Mercredi')).toBeChecked()
    expect(screen.getByLabelText('Jeudi')).toBeChecked()
    expect(screen.getByLabelText('Vendredi')).toBeChecked()
    expect(screen.getByLabelText('Samedi')).toBeChecked()
    expect(screen.getByLabelText('Dimanche')).toBeChecked()
  })

  it('should hide the "No end date" checkbox if the offer is not eligible to opening hours', async () => {
    renderStocksCalendarFormMultipleDays(
      {},
      getIndividualOfferFactory({ subcategoryId: SubcategoryIdEnum.CONFERENCE })
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.queryByLabelText('Pas de date de fin')
    ).not.toBeInTheDocument()
  })
})
