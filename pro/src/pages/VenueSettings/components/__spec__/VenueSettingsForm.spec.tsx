import { screen, waitFor } from '@testing-library/react'
import { FormProvider, useForm } from 'react-hook-form'
import { describe, expect, it, vi } from 'vitest'

import * as apiAdresse from '@/apiClient/adresse/apiAdresse'
import { api } from '@/apiClient/api'
import {
  type GetVenueResponseModel,
  VenueTypeCode,
  type VenueTypeResponseModel,
} from '@/apiClient/v1'
import { defaultGetVenue } from '@/commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  defaultVenueProvider,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import { toFormValues } from '@/pages/VenueSettings/commons/utils/toFormValues'

import type { VenueSettingsFormContext } from '../../commons/types'
import type { VenueSettingsFormValuesType } from '../../commons/validationSchema'
import {
  VenueSettingsForm,
  type VenueSettingsFormProps,
} from '../VenueSettingsForm'

const firstVenueProvider = { ...defaultVenueProvider }
const secondVenueProvider = {
  id: 2,
  isActive: true,
  isFromAllocineProvider: true,
  lastSyncDate: null,
  venueId: 2,
  dateCreated: '2021-08-15T00:00:00Z',
  venueIdAtOfferProvider: 'allocine_id_1',
  provider: {
    name: 'Allociné',
    id: 13,
    hasOffererProvider: false,
    isActive: true,
    enabledForPro: true,
  },
  quantity: 0,
  isDuo: true,
  price: 0,
}

const venueTypes: VenueTypeResponseModel[] = [
  { value: 'ARTISTIC_COURSE', label: 'Cours et pratique artistiques' },
  { value: 'SCIENTIFIC_CULTURE', label: 'Culture scientifique' },
]

const defaultFormContext: VenueSettingsFormContext = {
  isCaledonian: false,
  withSiret: true,
  isVenueVirtual: false,
  siren: '123456789',
  isVenueActivityFeatureActive: false,
}

const defaultOfferer = {
  ...defaultGetOffererResponseModel,
  id: 12,
  siren: '123456789',
}

const defaultVenue: GetVenueResponseModel = {
  ...defaultGetVenue,
  name: 'Lieu de test',
  publicName: 'Lieu Exemple Public',
  location: {
    banId: '12345',
    id: 2,
    isVenueLocation: false,
    street: '123 Rue Principale',
    city: 'Ville Exemple',
    postalCode: '75001',
    inseeCode: '75111',
    isManualEdition: false,
    latitude: 48.8566,
    longitude: 2.3522,
  },
  venueType: { value: VenueTypeCode.CENTRE_CULTUREL, label: 'Centre culturel' },
  comment: 'Un lieu populaire pour les concerts et les événements',
  bookingEmail: 'contact@lieuexemple.com',
  withdrawalDetails:
    "Les retraits sont autorisés jusqu'à 24 heures avant l'événement.",
}

const venueProviders = [firstVenueProvider, secondVenueProvider]

const fakeOnSubmit = vi.fn()

const renderVenueSettingsForm = async (
  props?: Partial<VenueSettingsFormProps>,
  options: RenderWithProvidersOptions = {
    user: sharedCurrentUserFactory(),
  }
) => {
  const Wrapper = () => {
    const formContext = {
      ...defaultFormContext,
      ...(props?.formContext || {}),
    }
    const form = useForm({
      context: formContext,
      defaultValues: toFormValues({
        venue: {
          ...defaultVenue,
          ...(props?.venue || {}),
        },
      }),
    })
    return (
      <FormProvider {...form}>
        <form
          onSubmit={form.handleSubmit(
            (formValues: VenueSettingsFormValuesType) =>
              fakeOnSubmit(formValues)
          )}
          noValidate
        >
          <VenueSettingsForm
            offerer={defaultOfferer}
            venueTypes={venueTypes}
            venueProviders={venueProviders}
            venue={defaultGetVenue}
            formContext={formContext}
          />
        </form>
      </FormProvider>
    )
  }

  renderWithProviders(<Wrapper />, options)

  await waitFor(() => {
    screen.getByText('Informations administratives')
  })
}

describe('VenueSettingsForm', () => {
  beforeEach(() => {
    vi.spyOn(apiAdresse, 'getDataFromAddress').mockResolvedValue([
      {
        address: '',
        city: '',
        inseeCode: '',
        id: '',
        latitude: 1,
        longitude: 2,
        label: '',
        postalCode: '',
      },
    ])

    vi.spyOn(api, 'getProvidersByVenue').mockResolvedValue([
      {
        name: 'Ciné Office',
        id: 12,
        hasOffererProvider: false,
        isActive: true,
        enabledForPro: true,
      },
      {
        name: 'Allociné',
        id: 13,
        hasOffererProvider: false,
        isActive: true,
        enabledForPro: true,
      },
      {
        name: 'Ticket Buster',
        id: 14,
        hasOffererProvider: true,
        isActive: true,
        enabledForPro: true,
      },
    ])
  })

  it('renders all main sections', () => {
    renderVenueSettingsForm()

    expect(screen.getByText('Informations administratives')).toBeInTheDocument()
    expect(screen.getByLabelText(/Activité principale/)).toBeInTheDocument()
    expect(
      screen.getByText(
        'Cette adresse s’appliquera par défaut à toutes vos offres, vous pourrez la modifier à l’échelle de chaque offre.'
      )
    ).toBeInTheDocument()
  })

  it('should display the venue provider cards & add provider button', async () => {
    await renderVenueSettingsForm()

    const cineOfficeCard = screen.getByText('Ciné Office')
    const allocineCard = screen.getByText('Allociné')
    const addProviderButton = screen.getByRole('button', {
      name: 'Sélectionner un logiciel',
    })

    expect(cineOfficeCard).toBeInTheDocument()
    expect(allocineCard).toBeInTheDocument()
    expect(addProviderButton).toBeInTheDocument()
  })

  it('should render the venue settings form with venue data', async () => {
    await renderVenueSettingsForm({
      venue: {
        ...defaultVenue,
        siret: '123 456 789 01234',
      },
    })

    const siretField = await screen.findByRole('textbox', {
      name: /SIRET de la structure/,
    })
    const nameField = await screen.findByRole('textbox', {
      name: /Raison sociale/,
    })
    const publicNameField = await screen.findByRole('textbox', {
      name: /Nom public/,
    })
    const addressField = await screen.findByRole('combobox', {
      name: /Adresse postale/,
    })
    const withdrawalDetailsField = await screen.findByRole('textbox', {
      name: /Informations de retrait/,
    })
    const emailField = await screen.findByRole('textbox', {
      name: /Adresse email/,
    })

    expect(siretField).toBeInTheDocument()
    expect(nameField).toBeInTheDocument()
    expect(publicNameField).toBeInTheDocument()
    expect(addressField).toBeInTheDocument()
    expect(withdrawalDetailsField).toBeInTheDocument()
    expect(emailField).toBeInTheDocument()

    expect(siretField).toHaveValue('123 456 789 01234')
    expect(nameField).toHaveValue('Lieu de test')
    expect(publicNameField).toHaveValue('Lieu Exemple Public')
    expect(addressField).toHaveValue('123 Rue Principale 75001 Ville Exemple')
    expect(withdrawalDetailsField).toHaveValue(
      "Les retraits sont autorisés jusqu'à 24 heures avant l'événement."
    )
    expect(emailField).toHaveValue('contact@lieuexemple.com')
  })

  it('should not display the field "Activité principale" if FF is active', async () => {
    await renderVenueSettingsForm(
      {
        formContext: {
          ...defaultFormContext,
          isVenueActivityFeatureActive: true,
        },
      },
      { user: sharedCurrentUserFactory(), features: ['WIP_VENUE_ACTIVITY'] }
    )

    const mainActivity = screen.queryByRole('combobox', {
      name: 'Activité principale',
    })

    expect(mainActivity).not.toBeInTheDocument()
  })
})
