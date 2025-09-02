import { screen } from '@testing-library/react'
import { FormProvider, useForm } from 'react-hook-form'

import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  TimetableOpeningHoursActionsBar,
  type TimetableOpeningHoursActionsBarProps,
} from './TimetableOpeningHoursActionsBar'

const defaultProps: TimetableOpeningHoursActionsBarProps = {
  offer: getIndividualOfferFactory(),
  mode: OFFER_WIZARD_MODE.CREATION,
}

function renderTimetableOpeningHoursActionsBar(
  props?: Partial<TimetableOpeningHoursActionsBarProps>
) {
  function TimetableOpeningHoursActionsBarWrapper() {
    const form = useForm({
      defaultValues: {},
      mode: 'onTouched',
    })

    return (
      <FormProvider {...form}>
        <TimetableOpeningHoursActionsBar {...defaultProps} {...props} />
      </FormProvider>
    )
  }

  return renderWithProviders(<TimetableOpeningHoursActionsBarWrapper />)
}

describe('TimetableOpeningHoursActionsBar', () => {
  it('should show previous and next buttons when creating', () => {
    renderTimetableOpeningHoursActionsBar()

    expect(
      screen.getByRole('button', { name: 'Enregistrer et continuer' })
    ).toBeInTheDocument()

    expect(screen.getByRole('button', { name: 'Retour' })).toBeInTheDocument()
  })

  it('should show previous and next buttons when editing an offer', () => {
    renderTimetableOpeningHoursActionsBar({ mode: OFFER_WIZARD_MODE.EDITION })

    expect(
      screen.getByRole('button', { name: 'Enregistrer les modifications' })
    ).toBeInTheDocument()

    expect(
      screen.getByRole('button', { name: 'Annuler et quitter' })
    ).toBeInTheDocument()
  })

  it('should show previous buttons when reading the offer info', () => {
    renderTimetableOpeningHoursActionsBar({ mode: OFFER_WIZARD_MODE.READ_ONLY })

    expect(
      screen.getByRole('button', { name: 'Retour à la liste des offres' })
    ).toBeInTheDocument()
  })
})
