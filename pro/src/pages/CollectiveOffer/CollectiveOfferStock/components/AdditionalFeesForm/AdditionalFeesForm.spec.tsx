import { yupResolver } from '@hookform/resolvers/yup'
import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { addDays, format } from 'date-fns'
import { FormProvider, useForm } from 'react-hook-form'
import { axe } from 'vitest-axe'

import { CollectiveAdditionalFeeType } from '@/apiClient/v1'
import { FORMAT_ISO_DATE_ONLY } from '@/commons/utils/date'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  type CollectiveOfferStockFormValues,
  generateValidationSchema,
} from '../CollectiveOfferStockForm/validationSchema'
import { AdditionalFeesForm } from './AdditionalFeesForm'

function renderAdditionalFeesForm({
  initialValues,
  canEditDiscount = true,
  onSubmit = vi.fn(),
}: {
  initialValues: Partial<
    Pick<
      CollectiveOfferStockFormValues,
      'hasAdditionalFees' | 'collectiveAdditionalFees'
    >
  >
  canEditDiscount?: boolean
  onSubmit?: () => void
}) {
  function AdditionalFeesFormWrapper() {
    const tomorrow = format(addDays(new Date(), 1), FORMAT_ISO_DATE_ONLY)
    const nonFeesDefaultValues: Omit<
      CollectiveOfferStockFormValues,
      'hasAdditionalFees' | 'collectiveAdditionalFees'
    > = {
      startDate: tomorrow,
      endDate: tomorrow,
      eventTime: '10:00',
      bookingLimitDate: tomorrow,
      numberOfTeachers: 1,
      numberOfTickets: 50,
      servicePrice: 100,
    }
    const form = useForm<CollectiveOfferStockFormValues>({
      defaultValues: { ...nonFeesDefaultValues, ...initialValues },
      resolver: yupResolver(generateValidationSchema(true)),
    })

    return (
      <FormProvider {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)}>
          <AdditionalFeesForm canEditDiscount={canEditDiscount} />
          <button type="submit">Enregistrer</button>
        </form>
      </FormProvider>
    )
  }

  return renderWithProviders(<AdditionalFeesFormWrapper />)
}

describe('AdditionalFeesForm', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderAdditionalFeesForm({
      initialValues: { hasAdditionalFees: false, collectiveAdditionalFees: [] },
    })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should not display additional fees fields when hasAdditionalFees is false', () => {
    renderAdditionalFeesForm({
      initialValues: { hasAdditionalFees: false, collectiveAdditionalFees: [] },
    })

    expect(
      screen.queryByLabelText(/Type de frais annexes/)
    ).not.toBeInTheDocument()
  })

  it('should display additional fee rows when hasAdditionalFees is true', () => {
    renderAdditionalFeesForm({
      initialValues: {
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          { type: CollectiveAdditionalFeeType.OTHER, label: 'toto', amount: 5 },
          {
            type: CollectiveAdditionalFeeType.ACCOMMODATION,
            label: '',
            amount: 10,
          },
        ],
      },
    })

    expect(screen.getAllByLabelText(/Type de frais annexes/)).toHaveLength(2)
    expect(screen.getAllByLabelText(/Prix \(en €\)/)).toHaveLength(2)
  })

  it('should add a row with default values and focus it when clicking "Oui"', async () => {
    const user = userEvent.setup()
    renderAdditionalFeesForm({
      initialValues: { hasAdditionalFees: false, collectiveAdditionalFees: [] },
    })

    await user.click(screen.getByRole('radio', { name: 'Oui' }))

    expect(screen.getAllByLabelText(/Type de frais annexes/)).toHaveLength(1)
    expect(screen.getByLabelText(/Prix \(en €\)/)).toHaveValue(0)
  })

  it('should clear all fees and hide fields when clicking "Non"', async () => {
    const user = userEvent.setup()
    renderAdditionalFeesForm({
      initialValues: {
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          {
            type: CollectiveAdditionalFeeType.ACCOMMODATION,
            label: null,
            amount: 50,
          },
        ],
      },
    })

    expect(screen.getByLabelText(/Type de frais annexes/)).toBeVisible()

    await user.click(screen.getByRole('radio', { name: 'Non' }))

    expect(
      screen.queryByLabelText(/Type de frais annexes/)
    ).not.toBeInTheDocument()
  })

  it('should add a new row when clicking "Ajouter un type de frais annexes"', async () => {
    const user = userEvent.setup()
    renderAdditionalFeesForm({
      initialValues: {
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          { type: CollectiveAdditionalFeeType.OTHER, label: '', amount: 0 },
        ],
      },
    })

    expect(screen.getAllByLabelText(/Type de frais annexes/)).toHaveLength(1)

    await user.click(
      screen.getByRole('button', { name: 'Ajouter un type de frais annexes' })
    )

    expect(screen.getAllByLabelText(/Type de frais annexes/)).toHaveLength(2)
  })

  it('should not allow adding more than a max number fee rows', () => {
    renderAdditionalFeesForm({
      initialValues: {
        hasAdditionalFees: true,
        collectiveAdditionalFees: Array.from({ length: 12 }, () => ({
          type: CollectiveAdditionalFeeType.OTHER,
          label: '',
          amount: 0,
        })),
      },
    })

    expect(
      screen.queryByRole('button', { name: 'Ajouter un type de frais annexes' })
    ).not.toBeInTheDocument()
  })

  it('should not allow adding when canEditDiscout is false', () => {
    renderAdditionalFeesForm({
      initialValues: {
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          { type: CollectiveAdditionalFeeType.OTHER, label: '', amount: 0 },
        ],
      },
      canEditDiscount: false,
    })

    expect(
      screen.queryByRole('button', { name: 'Ajouter un type de frais annexes' })
    ).not.toBeInTheDocument()
  })

  it('should remove a row when clicking the trash button', async () => {
    const user = userEvent.setup()
    renderAdditionalFeesForm({
      initialValues: {
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          {
            type: CollectiveAdditionalFeeType.ACCOMMODATION,
            label: null,
            amount: 10,
          },
          {
            type: CollectiveAdditionalFeeType.MEAL,
            label: null,
            amount: 12,
          },
          {
            type: CollectiveAdditionalFeeType.TRAVEL,
            label: null,
            amount: 20,
          },
        ],
      },
    })

    expect(screen.getAllByLabelText(/Type de frais annexes/)).toHaveLength(3)
    expect(screen.getAllByLabelText(/Prix \(en €\)/)).toHaveLength(3)

    const trashButtons = screen.getAllByRole('button', {
      name: 'Supprimer ce champ',
    })
    await user.click(trashButtons[1])

    expect(screen.getAllByLabelText(/Type de frais annexes/)).toHaveLength(2)
    const feeAmountInputs = screen.getAllByLabelText(/Prix \(en €\)/)
    expect(feeAmountInputs).toHaveLength(2)
    await waitFor(() => expect(feeAmountInputs[1]).toHaveFocus())
  })

  it('should not display the trash button when only one row remains', () => {
    renderAdditionalFeesForm({
      initialValues: {
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          { type: CollectiveAdditionalFeeType.OTHER, label: '', amount: 0 },
        ],
      },
    })

    expect(
      screen.queryByRole('button', { name: 'Supprimer ce champ' })
    ).not.toBeInTheDocument()
  })

  it('should disable the type and amount fields when canEditDiscount is false', () => {
    renderAdditionalFeesForm({
      initialValues: {
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          { type: CollectiveAdditionalFeeType.OTHER, label: '', amount: 0 },
        ],
      },
      canEditDiscount: false,
    })

    expect(screen.getByRole('radio', { name: 'Oui' })).toBeDisabled()
    expect(screen.getByRole('radio', { name: 'Non' })).toBeDisabled()
    expect(screen.getByLabelText(/Type de frais annexes/)).toBeDisabled()
    expect(screen.getByLabelText(/Prix \(en €\)/)).toBeDisabled()
  })

  it('should select a predefined fee type from the options', async () => {
    const user = userEvent.setup()
    renderAdditionalFeesForm({
      initialValues: {
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          { type: CollectiveAdditionalFeeType.OTHER, label: '', amount: 0 },
        ],
      },
    })

    const typeInput = screen.getByLabelText(/Type de frais annexes/)
    await user.click(typeInput)
    await user.click(screen.getByText("Hébergement de l'intervenant"))

    expect(typeInput).toHaveValue("Hébergement de l'intervenant")
  })

  it('should set type to OTHER and store the label when typing a custom value', async () => {
    const user = userEvent.setup()
    renderAdditionalFeesForm({
      initialValues: {
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          { type: CollectiveAdditionalFeeType.OTHER, label: '', amount: 0 },
        ],
      },
    })

    const typeInput = screen.getByLabelText(/Type de frais annexes/)
    await user.type(typeInput, 'Matos')

    await waitFor(() => {
      expect(screen.getByText('Ajouter "Matos"')).toBeVisible()
    })
  })

  it('should submit changes when fees are updated', async () => {
    const user = userEvent.setup()
    const onSubmit = vi.fn()
    renderAdditionalFeesForm({
      initialValues: {
        hasAdditionalFees: true,
        collectiveAdditionalFees: [
          { type: CollectiveAdditionalFeeType.OTHER, label: '', amount: 0 },
        ],
      },
      onSubmit,
    })

    await user.type(screen.getByLabelText(/Type de frais annexes/), 'Matos')
    await user.click(screen.getByText('Ajouter "Matos"'))
    const amountInput = screen.getByLabelText(/Prix \(en €\)/)
    await user.clear(amountInput)
    await user.type(amountInput, '12')

    await user.click(screen.getByRole('button', { name: 'Enregistrer' }))

    expect(onSubmit).toHaveBeenCalledExactlyOnceWith(
      expect.objectContaining({
        collectiveAdditionalFees: [
          {
            type: CollectiveAdditionalFeeType.OTHER,
            label: 'Matos',
            amount: 12,
          },
        ],
      }),
      expect.anything()
    )
  })
})
