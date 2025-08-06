import * as Dialog from '@radix-ui/react-dialog'
import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { SynchronizationEvents } from '@/commons/core/FirebaseEvents/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  GenericCinemaProviderForm,
  GenericCinemaProviderFormProps,
  GenericCinemaProviderFormValues,
} from './GenericCinemaProviderForm'

const mockLogEvent = vi.fn()

const renderCinemaProviderForm = async (
  props: GenericCinemaProviderFormProps
) => {
  renderWithProviders(
    <Dialog.Root defaultOpen>
      <Dialog.Content aria-describedby={undefined}>
        <GenericCinemaProviderForm {...props} />
      </Dialog.Content>
    </Dialog.Root>
  )

  await waitFor(() => screen.getByText('Accepter les réservations “Duo“'))
}

describe('GenericCinemaProviderForm', () => {
  let props: GenericCinemaProviderFormProps
  const providerId = 66
  const venueId = 1
  const offererId = 3

  beforeEach(() => {
    props = {
      saveVenueProvider: vi.fn().mockReturnValue(true),
      providerId: providerId,
      venueId: venueId,
      offererId: offererId,
      isCreatedEntity: true,
      onCancel: vi.fn(),
      initialValues: {
        isDuo: true,
        price: 10,
        quantity: 100,
        isActive: true,
      } as GenericCinemaProviderFormValues,
    }

    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      ...vi.importActual('@/app/App/analytics/firebase'),
      logEvent: mockLogEvent,
    }))
  })

  describe('import form cinema provider for the first time', () => {
    it('should display the isDuo checkbox checked by default', async () => {
      await renderCinemaProviderForm(props)

      const isDuoCheckbox = screen.getByLabelText(
        /Accepter les réservations “Duo“/
      )
      expect(isDuoCheckbox).toBeInTheDocument()
      expect(isDuoCheckbox).toBeChecked()
    })

    it('should display import button', async () => {
      await renderCinemaProviderForm(props)

      const offerImportButton = screen.getByRole('button', {
        name: 'Lancer la synchronisation',
      })
      expect(offerImportButton).toBeInTheDocument()
    })

    it('should track on import', async () => {
      await renderCinemaProviderForm(props)
      const offersImportButton = screen.getByRole('button', {
        name: 'Lancer la synchronisation',
      })

      await userEvent.click(offersImportButton)

      await waitFor(() => {
        expect(mockLogEvent).toHaveBeenCalledTimes(1)
        expect(mockLogEvent).toHaveBeenNthCalledWith(
          1,
          SynchronizationEvents.CLICKED_IMPORT,
          {
            offererId: offererId,
            venueId: venueId,
            providerId: providerId,
            saved: true,
          }
        )
      })
    })
  })

  describe('edit existing cinema provider', () => {
    beforeEach(() => {
      props.isCreatedEntity = false
      props.initialValues = {
        isDuo: false,
        isActive: false,
        price: 10,
        quantity: 100,
      }
    })

    it('should display modify and cancel button', async () => {
      await renderCinemaProviderForm(props)

      const saveEditionProvider = screen.getByRole('button', {
        name: 'Modifier',
      })
      expect(saveEditionProvider).toBeInTheDocument()

      const cancelEditionProvider = screen.getByRole('button', {
        name: 'Annuler',
      })
      expect(cancelEditionProvider).toBeInTheDocument()
    })

    it('should show existing parameters', async () => {
      await renderCinemaProviderForm(props)

      const isDuoCheckbox = screen.getByLabelText(
        /Accepter les réservations “Duo“/
      )
      expect(isDuoCheckbox).not.toBeChecked()
    })
  })

  describe('edit existing allocine provider', () => {
    beforeEach(() => {
      props.isCreatedEntity = false
      props.initialValues = {
        isDuo: false,
        isActive: false,
        price: 10,
        quantity: 100,
      }
      props.showAdvancedFields = true
    })

    it('should display allocine advanced fields', async () => {
      await renderCinemaProviderForm(props)

      const priceInput = screen.getByText(/Prix de vente\/place/)
      expect(priceInput).toBeInTheDocument()

      const callout = screen.getByText(
        'Pour le moment, seules les séances "classiques" peuvent être importées. Les séances spécifiques (3D, Dolby Atmos, 4DX...) ne génèreront pas d’offres. Nous travaillons actuellement à l’ajout de séances spécifiques.'
      )

      expect(callout).toBeInTheDocument()
    })

    it('should call onChange when the input value changes', async () => {
      await renderCinemaProviderForm(props)

      const input = screen.getByLabelText('Nombre de places/séance')

      await userEvent.clear(input)
      await userEvent.type(input, '10')

      await waitFor(() => {
        expect(input).toHaveValue(10)
      })
    })

    it('should include price and quantity in payload when showAdvancedFields is true', async () => {
      const saveVenueProvider = vi.fn().mockResolvedValue(true)

      const propsWithAdvancedFields = {
        ...props,
        showAdvancedFields: true,
        saveVenueProvider,
      }

      await renderCinemaProviderForm(propsWithAdvancedFields)

      const priceInput = screen.getByLabelText(/Prix de vente\/place/)
      const quantityInput = screen.getByLabelText('Nombre de places/séance')

      await userEvent.clear(priceInput)
      await userEvent.type(priceInput, '15.5')

      await userEvent.clear(quantityInput)
      await userEvent.type(quantityInput, '42')

      const submitButton = screen.getByRole('button', {
        name: /Lancer la synchronisation|Modifier/,
      })

      await userEvent.click(submitButton)

      await waitFor(() => {
        expect(saveVenueProvider).toHaveBeenCalledWith(
          expect.objectContaining({
            price: 15.5,
            quantity: 42,
          })
        )
      })
    })

    it('should omit quantity when not provided, even if showAdvancedFields is true', async () => {
      const saveVenueProvider = vi.fn().mockResolvedValue(true)

      props.showAdvancedFields = true
      props.saveVenueProvider = saveVenueProvider
      props.initialValues = {
        isDuo: false,
        isActive: false,
        price: 10,
        quantity: null,
      }

      await renderCinemaProviderForm(props)

      const submitButton = screen.getByRole('button', {
        name: /Lancer la synchronisation|Modifier/,
      })

      await userEvent.click(submitButton)

      await waitFor(() => {
        expect(saveVenueProvider).toHaveBeenCalledWith(
          expect.objectContaining({
            price: expect.any(Number),
            quantity: undefined,
          })
        )
      })
    })
  })
})
