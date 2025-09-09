import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'
import { vi } from 'vitest'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
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
  }
> = (params) => {
  const offer = params.offer ?? getIndividualOfferFactory({ id: 1 })

  const contextValues: PriceTableFormContext = {
    isCaledonian: params.contextValues?.isCaledonian ?? false,
    mode: params.contextValues?.mode ?? OFFER_WIZARD_MODE.CREATION,
    offer,
    ...params.contextValues,
  }
  const props: PriceTableFormProps = {
    isCaledonian: contextValues.isCaledonian,
    isReadOnly: params.props?.isReadOnly ?? false,
    mode: contextValues.mode,
    offer,
    schemaValidationContext: contextValues,
    offerStocks: [],
    ...params.props,
  }

  const Wrapper = () => {
    const form = useForm<PriceTableFormValues>({
      defaultValues: {
        entries: [
          {
            activationCodes: [],
            activationCodesExpirationDatetime: '',
            bookingLimitDatetime: '',
            bookingsQuantity: undefined,
            id: undefined,
            label: offer.isEvent ? 'Normal' : undefined,
            price: 10,
            quantity: offer.isEvent ? null : 5,
            offerId: offer.id,
            remainingQuantity: null,
          },
        ],
        isDuo: offer.isEvent ? true : null,
      },
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
    submitActivationCodes: 'Valider',
  },
  fields: {
    price: 'Prix',
    label: 'Intitulé du tarif',
    stock: 'Stock',
  },
}

describe('PriceTableForm', () => {
  const eventOffer = getIndividualOfferFactory({ isEvent: true })
  const nonEventOffer = getIndividualOfferFactory({ isEvent: false })

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
    const Wrapper = () => {
      const form = useForm<PriceTableFormValues>({
        defaultValues: {
          entries: [
            {
              activationCodes: [],
              activationCodesExpirationDatetime: '',
              bookingLimitDatetime: '',
              bookingsQuantity: 2,
              id: 10,
              label: undefined,
              price: 15,
              quantity: 8,
              offerId: offer.id,
              remainingQuantity: 6,
            },
          ],
          isDuo: null,
        },
        context: {
          isCaledonian: false,
          mode: OFFER_WIZARD_MODE.EDITION,
          offer,
        },
      })
      return (
        <FormProvider {...form}>
          <PriceTableForm
            isCaledonian={false}
            mode={OFFER_WIZARD_MODE.EDITION}
            offer={offer as GetIndividualOfferWithAddressResponseModel}
            offerStocks={[]}
            schemaValidationContext={{
              isCaledonian: false,
              mode: OFFER_WIZARD_MODE.EDITION,
              offer,
            }}
          />
        </FormProvider>
      )
    }
    renderWithProviders(<Wrapper />)

    expect(screen.getByText('Stock restant')).toBeInTheDocument()
    expect(screen.getByText('Réservations')).toBeInTheDocument()
  })

  it('should open confirmation dialog before deleting existing stock with bookings in EDITION mode and then remove it', async () => {
    const offer = { ...nonEventOffer, isEvent: false }
    const Wrapper = () => {
      const form = useForm<PriceTableFormValues>({
        defaultValues: {
          entries: [
            {
              activationCodes: [],
              activationCodesExpirationDatetime: '',
              bookingLimitDatetime: '',
              bookingsQuantity: 3,
              id: 42,
              label: undefined,
              price: 20,
              quantity: 10,
              offerId: offer.id,
              remainingQuantity: 7,
            },
            {
              activationCodes: [],
              activationCodesExpirationDatetime: '',
              bookingLimitDatetime: '',
              bookingsQuantity: 0,
              id: 43,
              label: undefined,
              price: 25,
              quantity: 5,
              offerId: offer.id,
              remainingQuantity: 5,
            },
          ],
          isDuo: null,
        },
        context: {
          isCaledonian: false,
          mode: OFFER_WIZARD_MODE.EDITION,
          offer,
        },
      })

      return (
        <FormProvider {...form}>
          <PriceTableForm
            isCaledonian={false}
            mode={OFFER_WIZARD_MODE.EDITION}
            offer={offer as GetIndividualOfferWithAddressResponseModel}
            offerStocks={[]}
            schemaValidationContext={{
              isCaledonian: false,
              mode: OFFER_WIZARD_MODE.EDITION,
              offer,
            }}
          />
        </FormProvider>
      )
    }
    renderWithProviders(<Wrapper />)

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

    expect(screen.getAllByLabelText(/Stock/)).toHaveLength(1)
  })

  it('should upload activation codes and set quantity accordingly', async () => {
    const offer = { ...nonEventOffer, isDigital: true }
    const Wrapper = () => {
      const form = useForm<PriceTableFormValues>({
        defaultValues: {
          entries: [
            {
              activationCodes: [],
              activationCodesExpirationDatetime: '',
              bookingLimitDatetime: '',
              bookingsQuantity: undefined,
              id: 55,
              label: undefined,
              price: 12,
              quantity: null,
              offerId: offer.id,
              remainingQuantity: null,
            },
          ],
          isDuo: null,
        },
        context: {
          isCaledonian: false,
          mode: OFFER_WIZARD_MODE.EDITION,
          offer,
        },
      })
      return (
        <FormProvider {...form}>
          <PriceTableForm
            isCaledonian={false}
            mode={OFFER_WIZARD_MODE.EDITION}
            offerStocks={[]}
            offer={offer as GetIndividualOfferWithAddressResponseModel}
            schemaValidationContext={{
              isCaledonian: false,
              mode: OFFER_WIZARD_MODE.EDITION,
              offer,
            }}
          />
        </FormProvider>
      )
    }
    renderWithProviders(<Wrapper />)

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
    const Wrapper = () => {
      const form = useForm<PriceTableFormValues>({
        defaultValues: {
          entries: [
            {
              activationCodes: [],
              activationCodesExpirationDatetime: '',
              bookingLimitDatetime: '',
              bookingsQuantity: 3,
              id: 101,
              label: undefined,
              price: 10,
              quantity: 5,
              offerId: offer.id,
              remainingQuantity: 5,
            },
            {
              activationCodes: [],
              activationCodesExpirationDatetime: '',
              bookingLimitDatetime: '',
              bookingsQuantity: 0,
              id: 102,
              label: undefined,
              price: 12,
              quantity: 6,
              offerId: offer.id,
              remainingQuantity: 6,
            },
          ],
          isDuo: null,
        },
        context: {
          isCaledonian: false,
          mode: OFFER_WIZARD_MODE.EDITION,
          offer,
        },
      })
      return (
        <FormProvider {...form}>
          <PriceTableForm
            isCaledonian={false}
            mode={OFFER_WIZARD_MODE.EDITION}
            offerStocks={[]}
            offer={offer as GetIndividualOfferWithAddressResponseModel}
            schemaValidationContext={{
              isCaledonian: false,
              mode: OFFER_WIZARD_MODE.EDITION,
              offer,
            }}
          />
        </FormProvider>
      )
    }
    renderWithProviders(<Wrapper />)

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
    renderPriceTableForm({
      offer,
      contextValues: { mode: OFFER_WIZARD_MODE.EDITION },
      props: { mode: OFFER_WIZARD_MODE.EDITION },
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
      name: 'Prix *',
    }) as HTMLInputElement
    await userEvent.clear(priceInput)
    await userEvent.type(priceInput, '23')
    expect(priceInput.value).toBe('23')

    const quantityInput = screen.getByRole('spinbutton', {
      name: /Stock/,
    }) as HTMLInputElement
    await userEvent.clear(quantityInput)
    await userEvent.type(quantityInput, '11')
    expect(quantityInput.value).toBe('11')
  })
})
