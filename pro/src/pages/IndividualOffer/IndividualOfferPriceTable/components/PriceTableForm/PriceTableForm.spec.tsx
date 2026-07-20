import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'
import { vi } from 'vitest'

import {
  type GetIndividualOfferWithAddressResponseModel,
  OfferStatus,
  VenueState,
} from '@/apiClient/v1'
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
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
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

const defaultSelectedPartnerVenue = makeGetVenueResponseModel({ id: 1 })

const renderPriceTableForm: RenderComponentFunction<
  PriceTableFormProps,
  PriceTableFormContext,
  {
    offer: GetIndividualOfferWithAddressResponseModel
    defaultValues?: PriceTableFormValues
    isVenueClosed?: boolean
  }
> = (params) => {
  const offer = params.offer ?? getIndividualOfferFactory({ id: 1 })
  const isVenueClosed = params.isVenueClosed ?? false

  const contextValues: PriceTableFormContext = {
    isCaledonian: params.contextValues?.isCaledonian ?? false,
    mode: params.contextValues?.mode ?? OFFER_WIZARD_MODE.CREATION,
    offer,
    ...params.contextValues,
  }
  const defaultValues: PriceTableFormValues = params.defaultValues ?? {
    priceCategories: [
      {
        activationCodes: [],
        activationCodesExpirationDatetime: null,
        bookingLimitDatetime: null,
        bookingsQuantity: null,
        hasActivationCode: false,
        hasStocks: null,
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

  return renderWithProviders(<Wrapper />, {
    storeOverrides: {
      user: {
        currentUser: sharedCurrentUserFactory(),
        selectedPartnerVenue: isVenueClosed
          ? makeGetVenueResponseModel({ id: 1, state: VenueState.CLOSED })
          : defaultSelectedPartnerVenue,
      },
    },
  })
}

const LABELS = {
  buttons: {
    activationTooltip: "Ajouter des codes d'activation",
    addEntry: 'Ajouter un tarif',
    cancelEntryRemoval: 'Annuler',
    closeModal: 'Fermer la fenêtre modale',
    confirmEntryRemoval: 'Confirmer la suppression',
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
  const entryBase: PriceTableFormValues['priceCategories'][0] = {
    activationCodes: null,
    activationCodesExpirationDatetime: null,
    bookingLimitDatetime: null,
    bookingsQuantity: null,
    hasActivationCode: false,
    hasStocks: null,
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
      priceCategories: [
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

  it('should ask for confirmation before deleting a price category with some stocks in CREATION mode', async () => {
    const offer = { ...nonEventOffer, isEvent: true }
    const contextValues = { mode: OFFER_WIZARD_MODE.CREATION }
    const props = { mode: OFFER_WIZARD_MODE.CREATION }
    const defaultValues = {
      priceCategories: [
        {
          ...entryBase,
          id: 1,
          hasStocks: true,
        },
        {
          ...entryBase,
          id: 2,
          hasStocks: false,
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
      screen.getByRole('dialog', {
        name: 'Voulez-vous supprimer ce tarif ?',
      })
    ).toBeInTheDocument()

    // The user clicks "Annuler"
    await userEvent.click(
      screen.getByRole('button', { name: LABELS.buttons.cancelEntryRemoval })
    )

    expect(
      screen.getAllByRole('button', { name: LABELS.buttons.removeEntry })
    ).toHaveLength(2)

    await userEvent.click(deleteButtons[0])

    // The user clicks "Confirmer la suppression"
    await userEvent.click(
      screen.getByRole('button', {
        name: LABELS.buttons.confirmEntryRemoval,
      })
    )

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
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
      priceCategories: [
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
    await userEvent.type(priceInput, '23,2')
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
          priceCategories: [
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

    renderWithProviders(<Wrapper />, {
      storeOverrides: {
        user: { selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }) },
      },
    })

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
      priceCategories: [
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
      priceCategories: [
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
      priceCategories: [
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

  it('should disable all fields when venue is closed', () => {
    const offer = { ...eventOffer, status: OfferStatus.ACTIVE }
    renderPriceTableForm({ offer, isVenueClosed: true })

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
})
