import * as Dialog from '@radix-ui/react-dialog'
import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { addDays, format } from 'date-fns'
import { axe } from 'vitest-axe'

import { FORMAT_ISO_DATE_ONLY } from 'commons/utils/date'
import { priceCategoryFactory } from 'commons/utils/factories/individualApiFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { RecurrenceForm, RecurrenceFormProps } from '../RecurrenceForm'

const mockSubmit = vi.fn()

const defaultProps: RecurrenceFormProps = {
  handleSubmit: mockSubmit,
  priceCategories: [priceCategoryFactory()],
}

function renderRecurrenceForm(props: RecurrenceFormProps = defaultProps) {
  return renderWithProviders(
    <Dialog.Root defaultOpen>
      <Dialog.Content aria-describedby={undefined}>
        <RecurrenceForm {...props} />
      </Dialog.Content>
    </Dialog.Root>
  )
}

describe('RecurrenceForm', () => {
  it('should pass axe accessibility tests', async () => {
    const { container } = renderRecurrenceForm()
    expect(await axe(container)).toHaveNoViolations()
  })

  it('should submit', async () => {
    renderRecurrenceForm()

    await userEvent.type(
      screen.getByLabelText('Date de l’évènement *'),
      format(addDays(new Date(), 1), FORMAT_ISO_DATE_ONLY)
    )
    await userEvent.type(screen.getByLabelText('Horaire 1 *'), '12:00')
    await userEvent.type(
      screen.getByRole('spinbutton', {
        name: 'Nombre de places',
      }),
      '10'
    )
    await userEvent.type(screen.getByLabelText('Tarif *'), '21')
    await userEvent.type(
      screen.getByLabelText('Date limite de réservation', { exact: false }),
      '2'
    )

    await userEvent.click(screen.getByText('Valider'))
    expect(mockSubmit).toHaveBeenCalled()
  })

  it('should add and remove a beginning time', async () => {
    renderRecurrenceForm()

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
    const priceCategories = [
      priceCategoryFactory(),
      priceCategoryFactory(),
      priceCategoryFactory(),
    ]
    renderRecurrenceForm({ ...defaultProps, priceCategories: priceCategories })

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
    renderRecurrenceForm()

    await userEvent.click(screen.getByLabelText('Tous les jours'))
  })

  it('should render for weekly recurrence', async () => {
    renderRecurrenceForm()

    await userEvent.click(screen.getByLabelText('Toutes les semaines'))

    expect(screen.getByLabelText('Lundi')).toBeInTheDocument()
    expect(screen.getByLabelText('Mardi')).toBeInTheDocument()
    expect(screen.getByLabelText('Mercredi')).toBeInTheDocument()
    expect(screen.getByLabelText('Jeudi')).toBeInTheDocument()
    expect(screen.getByLabelText('Vendredi')).toBeInTheDocument()
    expect(screen.getByLabelText('Samedi')).toBeInTheDocument()
    expect(screen.getByLabelText('Dimanche')).toBeInTheDocument()
  })
})
