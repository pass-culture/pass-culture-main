import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
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

import { StocksCalendarFormTimeAndPrice } from './StocksCalendarFormTimeAndPrice'

vi.mock('apiClient/api', () => ({
  api: {
    getCategories: vi.fn(),
  },
}))

function renderStocksCalendarFormTimeAndPrice(
  defaultOptions?: Partial<StocksCalendarFormValues>,
  offer = getIndividualOfferFactory({
    subcategoryId: SubcategoryIdEnum.SALON,
  })
) {
  function StocksCalendarFormTimeAndPriceWrapper() {
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
          <StocksCalendarFormTimeAndPrice form={form} offer={offer} />
        </FormProvider>
      </IndividualOfferContextProvider>
    )
  }

  return renderWithProviders(<StocksCalendarFormTimeAndPriceWrapper />)
}

describe('StocksCalendarFormTimeAndPrice', () => {
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

  it('should show a time slot type radio group choice', async () => {
    renderStocksCalendarFormTimeAndPrice()

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.getByLabelText('Le public doit se présenter :')
    ).toBeInTheDocument()
  })

  it('should show an error callout when trying to set specific time slots for multplie days without an end date', async () => {
    renderStocksCalendarFormTimeAndPrice({
      durationType: DurationTypeOption.MULTIPLE_DAYS_WEEKS,
      timeSlotType: TimeSlotTypeOption.OPENING_HOURS,
      multipleDaysHasNoEndDate: true,
    })

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.queryByText(
        'En n’indiquant pas de date de fin, vous ne pouvez pas choisir l’option horaires précis.'
      )
    ).not.toBeInTheDocument()

    await userEvent.click(screen.getByLabelText(/À un horaire précis/))

    expect(
      screen.getByText(
        'En n’indiquant pas de date de fin, vous ne pouvez pas choisir l’option horaires précis.'
      )
    ).toBeInTheDocument()
  })

  it('should hide the time slot type choice if the offer is not eligible to opening hours', async () => {
    renderStocksCalendarFormTimeAndPrice(
      {
        durationType: DurationTypeOption.MULTIPLE_DAYS_WEEKS,
      },
      getIndividualOfferFactory({ subcategoryId: SubcategoryIdEnum.CONFERENCE })
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.queryByLabelText('Le public doit se présenter :')
    ).not.toBeInTheDocument()
  })

  it('should show an error callout when trying to add opening hours while the offer already has stocks', async () => {
    renderStocksCalendarFormTimeAndPrice(
      {
        durationType: DurationTypeOption.ONE_DAY,
        timeSlotType: TimeSlotTypeOption.OPENING_HOURS,
      },
      getIndividualOfferFactory({
        hasStocks: true,
        subcategoryId: SubcategoryIdEnum.SALON,
      })
    )

    await waitFor(() => {
      expect(screen.queryByText('Chargement en cours')).not.toBeInTheDocument()
    })

    expect(
      screen.getByText(
        'Pour ajouter des horaires d’ouverture, vous devez supprimer toutes les dates que vous avez déjà ajoutées.'
      )
    ).toBeInTheDocument()
  })
})
