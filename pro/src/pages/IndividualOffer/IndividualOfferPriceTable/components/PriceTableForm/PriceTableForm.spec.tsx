import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'
import { vi } from 'vitest'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { OfferStatus } from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
} from '@/commons/utils/factories/individualApiFactories'
import {
  type RenderComponentFunction,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import type { PriceTableFormValues } from '../../commons/schemas'
import type { PriceTableFormContext } from '../../commons/types'
import { PriceTableForm, type PriceTableFormProps } from './PriceTableForm'

vi.mock(
  '@/components/IndividualOffer/StocksThing/ActivationCodeFormDialog/ActivationCodeFileChecker',
  () => ({
    checkAndParseUploadedFile: vi.fn(async () => ({
      errorMessage: '',
      activationCodes: ['CODE1', 'CODE2', 'CODE3', 'CODE4'],
    })),
    fileReader: {},
  })
)

const renderPriceTableForm: RenderComponentFunction<
  PriceTableFormProps,
  PriceTableFormContext,
  {
    offer: GetIndividualOfferWithAddressResponseModel
    defaultValues?: PriceTableFormValues
  }
> = (params) => {
  const offer = params.offer ?? getIndividualOfferFactory({ id: 1 })

  const contextValues: PriceTableFormContext = {
    isCaledonian: params.contextValues?.isCaledonian ?? false,
    mode: params.contextValues?.mode ?? OFFER_WIZARD_MODE.CREATION,
    offer,
    ...params.contextValues,
  }
  const defaultValues: PriceTableFormValues = params.defaultValues ?? {
    entries: [
      {
        activationCodes: [],
        activationCodesExpirationDatetime: null,
        bookingLimitDatetime: null,
        bookingsQuantity: null,
        hasActivationCode: false,
        id: null,
        label: offer.isEvent ? 'Normal' : null,
        price: 10,
        quantity: offer.isEvent ? null : 5,
        offerId: offer.id,
        remainingQuantity: null,
      },
    ],
    isDuo: offer.isEvent ? true : null,
  }
  const props: PriceTableFormProps = {
    isCaledonian: contextValues.isCaledonian,
    isReadOnly: params.props?.isReadOnly ?? false,
    mode: contextValues.mode,
    offer,
    schemaValidationContext: contextValues,
    ...params.props,
  }

  const Wrapper = () => {
    const form = useForm<PriceTableFormValues>({
      defaultValues,
      context: contextValues,
    })

    return (
      <FormProvider {...form}>
        <PriceTableForm {...props} />
      </FormProvider>
    )
  }

  return renderWithProviders(<Wrapper />)
}

const LABELS = {
  buttons: {
    activationTooltip: "Ajouter des codes d'activation",
    addEntry: 'Ajouter un tarif',
    cancelEntryRemoval: 'Annuler',
    closeModal: 'Fermer la fenêtre modale',
    confirmEntryRemoval: 'Supprimer',
    removeEntry: 'Supprimer ce tarif',
    resetEntry: 'Réinitialiser les valeurs de ce tarif',
    submitActivationCodes: 'Valider',
  },
  fields: {
    price: /Prix/,
    label: /Intitulé du tarif/,
    stock: /Stock/,
  },
}

describe('PriceTableForm', () => {
  const eventOffer = getIndividualOfferFactory({
    id: 1,
    isEvent: true,
  })
  const nonEventOffer = getIndividualOfferFactory({
    id: 1,
    isEvent: false,
  })
  const entryBase: PriceTableFormValues['entries'][0] = {
    activationCodes: null,
    activationCodesExpirationDatetime: null,
    bookingLimitDatetime: null,
    bookingsQuantity: null,
    hasActivationCode: false,
    id: null,
    label: null,
    price: 0,
    quantity: null,
    offerId: 1,
    remainingQuantity: null,
  }

  it('should display first entry fields for event offer', () => {
    renderPriceTableForm({ offer: eventOffer })

    expect(screen.getByLabelText(LABELS.fields.label)).toBeInTheDocument()
    expect(screen.getByLabelText(/Prix/)).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: LABELS.buttons.addEntry })
    ).toBeInTheDocument()
  })

  it('should add a new price category row when clicking add tariff', async () => {
    renderPriceTableForm({ offer: eventOffer })

    await userEvent.click(
      screen.getByRole('button', { name: LABELS.buttons.addEntry })
    )
    expect(screen.getAllByLabelText(LABELS.fields.label)).toHaveLength(2)
  })

  it('should show stock input for non event offer and hide label/add button', () => {
    renderPriceTableForm({ offer: nonEventOffer })

    expect(screen.queryByLabelText(LABELS.fields.label)).not.toBeInTheDocument()
    expect(screen.getByLabelText(/Stock/)).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: LABELS.buttons.addEntry })
    ).not.toBeInTheDocument()
  })

  it('should show activation code button when digital non-event offer', async () => {
    const offer = { ...nonEventOffer, isDigital: true }

    renderPriceTableForm({ offer })

    const codeButton = screen.getByRole('button', {
      name: LABELS.buttons.activationTooltip,
    })

    await userEvent.click(codeButton)

    expect(codeButton).toBeInTheDocument()
  })

  it('should remove an entry directly when only client-side entries (no id)', async () => {
    renderPriceTableForm({ offer: eventOffer })

    await userEvent.click(
      screen.getByRole('button', { name: LABELS.buttons.addEntry })
    )

    const deleteButtons = screen.getAllByRole('button', {
      name: LABELS.buttons.removeEntry,
    })

    await userEvent.click(deleteButtons[0])

    expect(deleteButtons).toHaveLength(2)
    expect(screen.getAllByLabelText(LABELS.fields.label)).toHaveLength(1)
  })

  it('should rename remaining label to "Tarif unique" when deleting one of two event entries', async () => {
    renderPriceTableForm({ offer: eventOffer })

    await userEvent.click(
      screen.getByRole('button', { name: LABELS.buttons.addEntry })
    )
    expect(screen.getAllByLabelText(LABELS.fields.label)).toHaveLength(2)

    const deleteButtons = screen.getAllByRole('button', {
      name: LABELS.buttons.removeEntry,
    })
    await userEvent.click(deleteButtons[0])

    const remainingLabelInput = screen.getByLabelText(
      LABELS.fields.label
    ) as HTMLInputElement
    expect(remainingLabelInput.value).toBe('Tarif unique')
  })

  it('should display remaining stock and bookings fields in EDITION mode for non-event offer', () => {
    const offer = { ...nonEventOffer, isEvent: false }
    const contextValues = { mode: OFFER_WIZARD_MODE.EDITION }
    const props = { mode: OFFER_WIZARD_MODE.EDITION }
    const defaultValues = {
      entries: [
        {
          ...entryBase,
          bookingsQuantity: 2,
          id: 10,
          price: 15,
          quantity: 8,
          remainingQuantity: 6,
        },
      ],
      isDuo: null,
    }

    renderPriceTableForm({
      offer,
      contextValues,
      props,
      defaultValues,
    })

    expect(screen.getByText('Stock restant')).toBeInTheDocument()
    expect(screen.getByText('Réservations')).toBeInTheDocument()
  })

  it('should open confirmation dialog before deleting existing stock with bookings in EDITION mode and then remove it', async () => {
    const offer = { ...nonEventOffer, isEvent: false }
    const contextValues = { mode: OFFER_WIZARD_MODE.EDITION }
    const props = { mode: OFFER_WIZARD_MODE.EDITION }
    const defaultValues = {
      entries: [
        {
          ...entryBase,
          bookingsQuantity: 3,
          id: 42,
          price: 20,
          quantity: 10,
          remainingQuantity: 7,
        },
        {
          ...entryBase,
          id: 43,
          price: 25,
          quantity: 5,
          remainingQuantity: 5,
        },
      ],
      isDuo: null,
    }

    renderPriceTableForm({
      offer,
      contextValues,
      props,
      defaultValues,
    })

    const deleteButtons = screen.getAllByRole('button', {
      name: LABELS.buttons.removeEntry,
    })
    expect(deleteButtons).toHaveLength(2)

    await userEvent.click(deleteButtons[0])

    expect(
      screen.getByText('Voulez-vous supprimer ce stock ?')
    ).toBeInTheDocument()
    const confirmButton = screen.getByRole('button', {
      name: LABELS.buttons.confirmEntryRemoval,
    })
    await userEvent.click(confirmButton)

    expect(
      screen.queryByRole('button', {
        name: LABELS.buttons.removeEntry,
      })
    ).not.toBeInTheDocument()
  })

  it('should upload activation codes and set quantity accordingly', async () => {
    const offer = { ...nonEventOffer, isDigital: true }
    const contextValues = { mode: OFFER_WIZARD_MODE.EDITION }
    const props = { mode: OFFER_WIZARD_MODE.EDITION }
    const defaultValues = {
      entries: [
        {
          ...entryBase,
          price: 12,
        },
      ],
      isDuo: null,
    }

    renderPriceTableForm({
      offer,
      contextValues,
      props,
      defaultValues,
    })

    await userEvent.click(
      screen.getByRole('button', { name: LABELS.buttons.activationTooltip })
    )
    expect(
      screen.getByText('Ajouter des codes d’activation')
    ).toBeInTheDocument()

    const fileInput = screen.getByLabelText(
      'Importer un fichier .csv depuis l’ordinateur'
    ) as HTMLInputElement
    const file = new File(['CODE1\nCODE2\nCODE3\nCODE4'], 'codes.csv', {
      type: 'text/csv',
    })
    await userEvent.upload(fileInput, file)

    const confirmContainer = await screen.findByText(
      /Vous êtes sur le point d’ajouter 4 codes d’activation./
    )
    expect(confirmContainer).toBeInTheDocument()
    const validerButton = screen.getByRole('button', {
      name: LABELS.buttons.submitActivationCodes,
    })
    await userEvent.click(validerButton)

    const stockInput = (await screen.findByRole('spinbutton', {
      name: /Stock/,
    })) as HTMLInputElement
    expect(stockInput.value).toBe('4')
  })

  it('should cancel deletion when user clicks Annuler in confirmation dialog', async () => {
    const offer = { ...nonEventOffer, isEvent: false }
    const contextValues = { mode: OFFER_WIZARD_MODE.EDITION }
    const props = { mode: OFFER_WIZARD_MODE.EDITION }
    const defaultValues = {
      entries: [
        {
          ...entryBase,
          bookingsQuantity: 3,
          id: 101,
          price: 10,
          quantity: 5,
          remainingQuantity: 5,
        },
        {
          ...entryBase,
          id: 102,
          price: 12,
          quantity: 6,
          remainingQuantity: 6,
        },
      ],
      isDuo: null,
    }

    renderPriceTableForm({
      offer,
      contextValues,
      props,
      defaultValues,
    })

    const deleteButtons = screen.getAllByRole('button', {
      name: LABELS.buttons.removeEntry,
    })
    await userEvent.click(deleteButtons[0])
    expect(
      screen.getByRole('heading', { name: 'Voulez-vous supprimer ce stock ?' })
    ).toBeInTheDocument()
    await userEvent.click(
      screen.getByRole('button', { name: LABELS.buttons.cancelEntryRemoval })
    )
    expect(
      screen.getAllByRole('button', { name: LABELS.buttons.removeEntry })
    ).toHaveLength(2)
  })

  it('should cancel activation code dialog without modifying quantity', async () => {
    const offer = { ...nonEventOffer, isDigital: true }
    const contextValues = { mode: OFFER_WIZARD_MODE.EDITION }
    const props = { mode: OFFER_WIZARD_MODE.EDITION }

    renderPriceTableForm({
      offer,
      contextValues,
      props,
    })

    await userEvent.click(
      screen.getByRole('button', { name: LABELS.buttons.activationTooltip })
    )
    expect(
      screen.getByText('Ajouter des codes d’activation')
    ).toBeInTheDocument()

    await userEvent.click(
      screen.getByRole('button', { name: LABELS.buttons.closeModal })
    )
    expect(
      screen.queryByText('Ajouter des codes d’activation')
    ).not.toBeInTheDocument()

    const quantityInput = screen.getByRole('spinbutton', {
      name: /Stock/,
    }) as HTMLInputElement
    expect(quantityInput.value).toBe('5')
  })

  it('should update price and quantity fields on user input', async () => {
    const offer = { ...nonEventOffer, isEvent: false }
    renderPriceTableForm({ offer })

    const priceInput = screen.getByRole('spinbutton', {
      name: /Prix/,
    }) as HTMLInputElement
    await userEvent.clear(priceInput)
    await userEvent.type(priceInput, '23')
    expect(priceInput.value).toBe('23')

    await userEvent.clear(priceInput)
    await userEvent.type(priceInput, '23.2')
    expect(priceInput.value).toBe('23.2')

    const quantityInput = screen.getByRole('spinbutton', {
      name: /Stock/,
    }) as HTMLInputElement
    await userEvent.clear(quantityInput)
    await userEvent.type(quantityInput, '11')
    expect(quantityInput.value).toBe('11')
  })

  it('should update price fields on user input for Caledonian with correct currency', async () => {
    const offer = { ...nonEventOffer, isEvent: false }
    renderPriceTableForm({ offer, contextValues: { isCaledonian: true } })

    const priceInput = screen.getByRole('spinbutton', {
      name: /Prix/,
    }) as HTMLInputElement

    await userEvent.clear(priceInput)
    await userEvent.type(priceInput, '23.2')
    expect(priceInput.value).toBe('232')
  })

  it('should disable all inputs and actions when offer is pending (event offer)', () => {
    const offer = {
      ...eventOffer,
      status: OfferStatus.PENDING,
    }

    renderPriceTableForm({ offer })

    const labelInput = screen.getByLabelText(LABELS.fields.label)
    expect(labelInput).toBeDisabled()

    expect(
      screen.getByRole<HTMLInputElement>('spinbutton', {
        name: LABELS.fields.price,
      })
    ).toBeDisabled()

    expect(
      screen.queryByRole('button', {
        name: LABELS.buttons.addEntry,
      })
    ).not.toBeInTheDocument()
  })

  it('should allow editing quantity but not price when offer is synchronized (non Allociné, non-event)', async () => {
    const offer = {
      ...nonEventOffer,
      status: OfferStatus.ACTIVE,
      lastProvider: { name: 'SomeOtherProvider' },
    }

    renderPriceTableForm({ offer })

    const priceInput = screen.getByRole<HTMLInputElement>('spinbutton', {
      name: LABELS.fields.price,
    })
    expect(priceInput).toBeDisabled()

    const quantityInput = screen.getByRole<HTMLInputElement>('spinbutton', {
      name: /Stock/,
    })
    expect(quantityInput).not.toBeDisabled()

    await userEvent.clear(quantityInput)
    await userEvent.type(quantityInput, '9')
    expect(quantityInput.value).toBe('9')
  })

  it('should disable all fields when another published offer shares the same EAN', () => {
    const offer = {
      ...eventOffer,
      status: OfferStatus.ACTIVE,
    }

    const context: IndividualOfferContextValues = {
      ...individualOfferContextValuesFactory({ offer }),
      hasPublishedOfferWithSameEan: true,
    }

    const Wrapper = () => {
      const form = useForm<PriceTableFormValues>({
        defaultValues: {
          entries: [
            {
              activationCodes: null,
              activationCodesExpirationDatetime: null,
              bookingLimitDatetime: '',
              bookingsQuantity: undefined,
              id: undefined,
              label: 'Normal',
              price: 10,
              quantity: null,
              offerId: offer.id,
              remainingQuantity: null,
            },
          ],
          isDuo: true,
        },
        context: {
          isCaledonian: false,
          mode: OFFER_WIZARD_MODE.CREATION,
          offer,
        },
      })

      return (
        <IndividualOfferContext.Provider value={context}>
          <FormProvider {...form}>
            <PriceTableForm
              isCaledonian={false}
              mode={OFFER_WIZARD_MODE.CREATION}
              offer={offer as GetIndividualOfferWithAddressResponseModel}
              schemaValidationContext={{
                isCaledonian: false,
                mode: OFFER_WIZARD_MODE.CREATION,
                offer,
              }}
            />
          </FormProvider>
        </IndividualOfferContext.Provider>
      )
    }

    renderWithProviders(<Wrapper />)

    const labelInput = screen.getByLabelText(LABELS.fields.label)
    expect(labelInput).toBeDisabled()

    const priceInput = screen.getByRole<HTMLInputElement>('spinbutton', {
      name: LABELS.fields.price,
    })
    expect(priceInput).toBeDisabled()

    expect(
      screen.queryByRole('button', {
        name: LABELS.buttons.addEntry,
      })
    ).not.toBeInTheDocument()
  })

  it('should keep fields editable when synchronized via Allociné (non-event)', async () => {
    const offer = {
      ...nonEventOffer,
      status: OfferStatus.ACTIVE,
      lastProvider: { name: 'Allociné' },
    }

    renderPriceTableForm({ offer })

    const priceInput = screen.getByRole<HTMLInputElement>('spinbutton', {
      name: LABELS.fields.price,
    })
    expect(priceInput).not.toBeDisabled()
    await userEvent.clear(priceInput)
    await userEvent.type(priceInput, '33')
    expect(priceInput.value).toBe('33')

    const quantityInput = screen.getByRole<HTMLInputElement>('spinbutton', {
      name: /Stock/,
    })
    expect(quantityInput).not.toBeDisabled()
    await userEvent.clear(quantityInput)
    await userEvent.type(quantityInput, '12')
    expect(quantityInput.value).toBe('12')
  })

  it('should enable label editing once a second event entry is added', async () => {
    const offer = { ...eventOffer, status: OfferStatus.ACTIVE }
    renderPriceTableForm({ offer })

    const initialLabelInput = screen.getByLabelText(LABELS.fields.label)
    expect(initialLabelInput).toBeDisabled() // disabled when only one entry

    await userEvent.click(
      screen.getByRole('button', { name: LABELS.buttons.addEntry })
    )

    const labelInputs = screen.getAllByLabelText(LABELS.fields.label)
    expect(labelInputs.length).toBe(2)
    expect(labelInputs[0]).not.toBeDisabled()
    expect(labelInputs[1]).not.toBeDisabled()
  })

  it('should keep event labels disabled when synchronized via non-Allociné provider even with multiple entries', () => {
    const offer = {
      ...eventOffer,
      status: OfferStatus.ACTIVE,
      lastProvider: { name: 'SomeOtherProvider' },
    }
    const defaultValues = {
      entries: [
        {
          ...entryBase,
          label: 'Cat 1',
          price: 10,
        },
        {
          ...entryBase,
          label: 'Cat 2',
          price: 12,
        },
      ],
      isDuo: true,
    }

    renderPriceTableForm({ offer, defaultValues })

    const labelInputs = screen.getAllByLabelText(LABELS.fields.label)
    expect(labelInputs.length).toBe(2)
    expect(labelInputs[0]).toBeDisabled()
    expect(labelInputs[1]).toBeDisabled()

    const priceInputs = screen.getAllByRole('spinbutton', {
      name: /Prix/,
    })
    expect(priceInputs[0]).toBeDisabled()
  })

  it('should disable expiration date when entry has activationCodesExpirationDatetime', () => {
    const offer = {
      ...nonEventOffer,
      isDigital: true,
    }
    const defaultValues = {
      entries: [
        {
          ...entryBase,
          activationCodes: ['A', 'B'],
          activationCodesExpirationDatetime: '2025-12-31',
          price: 10,
          quantity: 2,
        },
      ],
      isDuo: null,
    }

    renderPriceTableForm({ offer, defaultValues })

    const expirationInput = screen.getByLabelText(
      /Date d'expiration/
    ) as HTMLInputElement
    expect(expirationInput).toBeDisabled()
    expect(expirationInput.value).toBe('2025-12-31')
  })

  it('should disable quantity input when activation codes are present', () => {
    const offer = { ...nonEventOffer, isDigital: true }
    const defaultValues = {
      entries: [
        {
          ...entryBase,
          activationCodes: ['A1', 'A2', 'A3'],
          hasActivationCode: true,
          price: 8,
          quantity: 3,
        },
      ],
      isDuo: null,
    }

    renderPriceTableForm({
      offer,
      defaultValues,
    })

    const quantityInput = screen.getByRole<HTMLInputElement>('spinbutton', {
      name: /Stock/,
    })
    expect(quantityInput).toBeDisabled()
  })

  it('should reset single event entry instead of removing it (label becomes "Tarif unique")', async () => {
    const offer = { ...eventOffer }
    renderPriceTableForm({ offer })

    const deleteButton = screen.getByRole('button', {
      name: LABELS.buttons.resetEntry,
    })
    await userEvent.click(deleteButton)

    const labelInput = screen.getByLabelText(
      LABELS.fields.label
    ) as HTMLInputElement
    expect(labelInput.value).toBe('Tarif unique')
  })

  it('should render activation button as disabled attribute when synchronized via non-Allociné (digital non-event)', () => {
    const offer = {
      ...nonEventOffer,
      isDigital: true,
      status: OfferStatus.ACTIVE,
      lastProvider: { name: 'SomeOtherProvider' },
    }

    renderPriceTableForm({ offer })

    expect(
      screen.queryByRole('button', {
        name: LABELS.buttons.activationTooltip,
      })
    ).toBeFalsy()
  })

  it('should not display remove/reset button for event offer in EDITION mode', () => {
    const offer = { ...eventOffer, status: OfferStatus.ACTIVE }
    const contextValues = { mode: OFFER_WIZARD_MODE.EDITION }
    const props = { mode: OFFER_WIZARD_MODE.EDITION }

    renderPriceTableForm({
      offer,
      contextValues,
      props,
    })

    expect(
      screen.queryByRole('button', {
        name: LABELS.buttons.resetEntry,
      })
    ).toBeFalsy()
  })

  it('should log an event when the limit date is updated', async () => {
    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    const offer = { ...nonEventOffer, status: OfferStatus.ACTIVE }

    renderPriceTableForm({
      offer,
    })

    const input = screen.getByLabelText('Date limite de réservation')
    await userEvent.type(input, '2020-12-15')
    await userEvent.click(screen.getByLabelText(/Prix/))

    expect(mockLogEvent).toHaveBeenCalledWith(
      Events.UPDATED_BOOKING_LIMIT_DATE,
      expect.objectContaining({ bookingLimitDatetime: '2020-12-15' })
    )
  })
})
