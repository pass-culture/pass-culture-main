import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { HasDateEnum } from '../../commons/types'
import {
  TimetableOpeningHours,
  type TimetableOpeningHoursProps,
} from './TimetableOpeningHours'

const defaultProps: TimetableOpeningHoursProps = {
  offer: getIndividualOfferFactory(),
  mode: OFFER_WIZARD_MODE.CREATION,
  timetableTypeRadioGroupShown: true,
}

function renderTimetableOpeningHours(
  props?: Partial<TimetableOpeningHoursProps>
) {
  function TimetableOpeningHoursWrapper() {
    const form = useForm({
      defaultValues: {
        timetableType: 'openingHours',
        quantityPerPriceCategories: [{ priceCategory: '1' }],
        openingHours: { MONDAY: null },
        hasStartDate: HasDateEnum.NO,
        hasEndDate: HasDateEnum.NO,
        startDate: null,
        endDate: null,
      },
      mode: 'onTouched',
    })

    return (
      <FormProvider {...form}>
        <TimetableOpeningHours {...defaultProps} {...props} />
      </FormProvider>
    )
  }

  return renderWithProviders(<TimetableOpeningHoursWrapper />)
}

describe('TimetableOpeningHours', () => {
  it('should render the opening hours form', () => {
    renderTimetableOpeningHours()

    waitFor(() => {
      screen.getByRole('radiogroup', {
        name: /Peut-on en profiter dès aujourd’hui/,
      })
    })

    expect(
      screen.getByRole('heading', { name: 'Horaires d’accès' })
    ).toBeInTheDocument()
  })

  it('should show the start date if the offer opening hours start in the future', async () => {
    renderTimetableOpeningHours()

    await userEvent.click(
      screen.getAllByRole('radio', {
        name: 'Oui',
      })[0]
    )

    expect(screen.getByLabelText('Date de début *')).toBeInTheDocument()
  })

  it('should show the end date if the offer opening hours end at some point', async () => {
    renderTimetableOpeningHours()

    await userEvent.click(
      screen.getAllByRole('radio', {
        name: 'Oui',
      })[1]
    )

    expect(screen.getByLabelText('Date de fin *')).toBeInTheDocument()
  })
})
