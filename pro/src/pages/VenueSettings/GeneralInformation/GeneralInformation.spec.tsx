import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { DisplayableActivity } from '@/apiClient/v1'
import type { GetVenueResponseModel } from '@/apiClient/v1/new'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import { Component as GeneralInformation } from './GeneralInformation'

vi.mock('@/commons/hooks/useSyncVenueCache', () => ({
  useSyncVenueCache: () => ({ syncVenueWithData: vi.fn() }),
}))

vi.mock('@/apiClient/api', () => ({
  apiNew: { editVenue: vi.fn(), getVenue: vi.fn() },
}))

vi.mock('@/commons/core/Venue/siretApiValidate')

vi.mock('@/commons/core/Venue/utils/getSiretData', () => ({
  getSiretData: vi.fn(),
}))

vi.mock('@/components/AddressFields/AddressFields', () => ({
  AddressFields: ({
    onManualChange,
    onAddressChosen,
  }: {
    onManualChange: () => void
    onAddressChosen: (
      data: import('@/apiClient/adresse/types').AdresseData
    ) => void
  }) => (
    <div data-testid="address-fields">
      <button type="button" onClick={onManualChange}>
        Entrer l'adresse manuellement
      </button>
      <button
        type="button"
        onClick={() =>
          onAddressChosen({
            address: '1 Rue de la Paix',
            city: 'Paris',
            inseeCode: '75056',
            id: 'ban-123',
            latitude: 48.8566,
            longitude: 2.3522,
            label: '1 Rue de la Paix 75001 Paris',
            postalCode: '75001',
          })
        }
      >
        Sélectionner une adresse
      </button>
    </div>
  ),
}))

const renderGeneralInformation = (
  venueOverrides: Partial<GetVenueResponseModel> = {},
  options?: RenderWithProvidersOptions
) => {
  const user = sharedCurrentUserFactory()

  const venue = {
    ...defaultGetVenue,
    publicName: 'Adresse de la venue',
    ...venueOverrides,
  }

  return renderWithProviders(<GeneralInformation />, {
    user,
    ...options,
    storeOverrides: {
      user: { currentUser: user, selectedPartnerVenue: venue },
      ...options?.storeOverrides,
    },
  })
}

describe('GeneralInformation', () => {
  it('should render the "Raison sociale" field as disabled', async () => {
    renderGeneralInformation({ id: 1 })

    const field = await screen.findByLabelText('Raison sociale')
    expect(field).toBeInTheDocument()
    expect(field).toBeDisabled()
  })

  it('should render the save button', async () => {
    renderGeneralInformation({ id: 1 })

    expect(
      await screen.findByRole('button', { name: /Enregistrer/ })
    ).toBeInTheDocument()
  })

  describe('when the venue is not virtual', () => {
    it('should render the administrative information section with SIRET and address fields', async () => {
      renderGeneralInformation({
        id: 1,
        siret: '12345678901234',
      })

      expect(
        await screen.findByText('Informations administratives')
      ).toBeInTheDocument()
      expect(screen.getByLabelText(/SIRET de la structure/)).toBeInTheDocument()
      expect(screen.getByLabelText('Nom public')).toBeInTheDocument()
      expect(screen.getByTestId('address-fields')).toBeInTheDocument()
    })

    it('should toggle manual address when clicking the manual address button', async () => {
      renderGeneralInformation({ id: 1 })

      await userEvent.click(
        await screen.findByText("Entrer l'adresse manuellement")
      )

      expect(screen.getByTestId('address-fields')).toBeInTheDocument()
    })

    it('should fill address fields when an address is selected', async () => {
      renderGeneralInformation({ id: 1 })

      await userEvent.click(await screen.findByText('Sélectionner une adresse'))

      expect(screen.getByTestId('address-fields')).toBeInTheDocument()
    })
  })

  describe('reimbursement section', () => {
    it('should render "Barème de remboursement" when venue has a pricing point', async () => {
      renderGeneralInformation({
        id: 1,
        pricingPoint: {
          id: 42,
          siret: '12345678901234',
          venueName: 'Ma structure',
        },
      })

      expect(
        await screen.findByText('Barème de remboursement')
      ).toBeInTheDocument()
    })

    it('should render "Barème de remboursement" when location has a hash', async () => {
      renderGeneralInformation({
        id: 1,
        pricingPoint: {
          id: 42,
          siret: '12345678901234',
          venueName: 'Ma structure',
        },
      })

      expect(
        await screen.findByText('Barème de remboursement')
      ).toBeInTheDocument()
    })

    it('should not render "Barème de remboursement" when venue has no pricing point', async () => {
      renderGeneralInformation({ id: 1, pricingPoint: null })

      await waitFor(() => {
        expect(
          screen.queryByText('Barème de remboursement')
        ).not.toBeInTheDocument()
      })
    })
  })
  describe('open to public toggle', () => {
    it('should display a mandatory toggle to define isOpenToPublic', async () => {
      renderGeneralInformation({ id: 1, isOpenToPublic: false })

      const toggle = screen.getByRole('group', {
        name: "Disposez-vous d'un lieu ouvert au public ?",
      })

      await waitFor(() => {
        expect(toggle).toBeInTheDocument()
      })
    })

    it('closed to public - should not show address section', () => {
      renderGeneralInformation({ id: 1, isOpenToPublic: false })

      expect(screen.queryByTestId('address-fields')).not.toBeInTheDocument()
    })

    it('open to public - should show address section', () => {
      renderGeneralInformation({ id: 1, isOpenToPublic: true })

      expect(screen.getByTestId('address-fields')).toBeInTheDocument()
    })

    it('switching to "Non" should show address section when activity is valid for NOT_OPEN_TO_PUBLIC', async () => {
      renderGeneralInformation({
        id: 1,
        isOpenToPublic: true,
        activity: DisplayableActivity.FESTIVAL,
      })

      await userEvent.click(await screen.findByRole('radio', { name: /Non/ }))

      expect(screen.queryByTestId('address-fields')).not.toBeInTheDocument()
      const activitySelect = screen.getByRole('combobox', {
        name: /Activité principale/,
      })
      expect(activitySelect).toHaveValue('FESTIVAL')
    })

    it('switching to "Non" should reset activity when it is not valid for NOT_OPEN_TO_PUBLIC', async () => {
      renderGeneralInformation({
        id: 1,
        isOpenToPublic: true,
        activity: DisplayableActivity.CULTURAL_CENTRE,
      })

      await userEvent.click(await screen.findByRole('radio', { name: /Non/ }))

      const activitySelect = screen.getByRole('combobox', {
        name: /Activité principale/,
      })
      expect(activitySelect).toHaveValue('')
    })

    it('switching to "Non" with no initial activity should not cause errors', async () => {
      renderGeneralInformation({
        id: 1,
        isOpenToPublic: true,
        activity: null,
      })

      await userEvent.click(await screen.findByRole('radio', { name: /Non/ }))

      const activitySelect = screen.getByRole('combobox', {
        name: /Activité principale/,
      })
      expect(activitySelect).toHaveValue('')
    })

    it('switching to "Oui" should show address section', async () => {
      renderGeneralInformation({ id: 1, isOpenToPublic: false })

      await userEvent.click(await screen.findByRole('radio', { name: /Oui/ }))

      expect(screen.getByTestId('address-fields')).toBeInTheDocument()
    })
  })
})
