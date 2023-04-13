import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { axe } from 'jest-axe'
import React from 'react'

import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import {
  individualOfferFactory,
  priceCategoryFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { RecurrenceForm } from '../RecurrenceForm'

const mockLogEvent = jest.fn()

const defaultProps = {
  offer: individualOfferFactory({ stocks: [] }),
  onCancel: jest.fn(),
  onConfirm: jest.fn(),
}

describe('RecurrenceForm', () => {
  beforeEach(() => {
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))
  })

  it('should pass axe accessibility tests', async () => {
    const { container } = renderWithProviders(
      <RecurrenceForm {...defaultProps} />
    )
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should submit', async () => {
    const onConfirm = jest.fn()
    renderWithProviders(
      <RecurrenceForm {...defaultProps} onConfirm={onConfirm} />
    )

    await userEvent.click(
      screen.getByLabelText('Date de l’évènement', { exact: true })
    )

    // There is a case where multiple dates can be displayed by the datepicker,
    // for instance the 27th of the previous month and the 27th of the current month.
    // We always choose the last one so that we are sure it's in the future
    const dates = screen.queryAllByText(new Date().getDate())
    await userEvent.click(dates[dates.length - 1])
    await userEvent.click(screen.getByLabelText('Horaire 1'))
    await userEvent.click(screen.getByText('12:00'))
    await userEvent.type(screen.getByLabelText('Nombre de places'), '10')
    await userEvent.type(screen.getByLabelText('Tarif'), '21')
    await userEvent.type(
      screen.getByLabelText('Date limite de réservation', { exact: false }),
      '2'
    )

    await userEvent.click(screen.getByText('Valider'))
    expect(onConfirm).toHaveBeenCalled()
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'stocks',
        isDraft: false,
        isEdition: true,
        offerId: '1',
        to: 'stocks',
        used: 'RecurrencePopin',
        recurrenceType: 'UNIQUE',
      }
    )
  })

  it('should add and remove a beginning time', async () => {
    renderWithProviders(<RecurrenceForm {...defaultProps} />)

    expect(
      screen.getByRole('button', { name: 'Supprimer le créneau' })
    ).toBeDisabled()

    await userEvent.click(screen.getByText('Ajouter un créneau'))

    const deleteButton = screen.getAllByRole('button', {
      name: 'Supprimer le créneau',
    })[0]
    expect(deleteButton).toBeEnabled()

    await userEvent.click(deleteButton)

    expect(
      screen.getByRole('button', { name: 'Supprimer le créneau' })
    ).toBeDisabled()
  })

  it('should show an add button until we have less or an equal number of fields than different price_categories', async () => {
    defaultProps.offer.priceCategories = [
      priceCategoryFactory(),
      priceCategoryFactory(),
      priceCategoryFactory(),
    ]
    renderWithProviders(<RecurrenceForm {...defaultProps} />)

    await userEvent.click(screen.getByText('Ajouter d’autres places et tarifs'))
    const deleteButton = screen.getAllByRole('button', {
      name: 'Supprimer les places',
    })[0]
    expect(deleteButton).toBeEnabled()
    await userEvent.click(screen.getByText('Ajouter d’autres places et tarifs'))
    expect(
      screen.queryByText('Ajouter d’autres places et tarifs')
    ).not.toBeInTheDocument()

    await userEvent.click(deleteButton)
    await userEvent.click(deleteButton)

    expect(
      screen.getByRole('button', { name: 'Supprimer les places' })
    ).toBeDisabled()
  })

  it('should render for daily recurrence', async () => {
    renderWithProviders(<RecurrenceForm {...defaultProps} />)

    await userEvent.click(screen.getByLabelText('Tous les jours'))
  })
})
