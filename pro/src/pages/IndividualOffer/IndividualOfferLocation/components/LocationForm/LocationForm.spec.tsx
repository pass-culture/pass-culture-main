import { screen } from '@testing-library/react'
import { FormProvider, useForm } from 'react-hook-form'
import { axe } from 'vitest-axe'

import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  makeVenueListItem,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderComponentFunction,
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'
import {
  MOCKED_SUBCATEGORIES,
  MOCKED_SUBCATEGORY,
} from '@/pages/IndividualOffer/commons/__mocks__/constants'

import type { LocationFormValues } from '../../commons/types'
import { LocationForm, type LocationFormProps } from './LocationForm'

const LABELS = {
  sectionTitles: {
    location: /Où profiter de l’offre ?/,
  },
  fields: {
    offerLocation:
      'Il s’agit de l’adresse à laquelle les jeunes devront se présenter.',
    url: 'URL d’accès à l’offre *',
  },
}

vi.mock('@/apiClient/api', () => ({
  api: {
    getCategories: vi.fn(),
    bulkCreateEventStocks: vi.fn(),
  },
}))

const renderLocationForm: RenderComponentFunction<
  LocationFormProps,
  IndividualOfferContextValues,
  {
    formDefaultValues?: Partial<LocationFormValues>
  }
> = (params) => {
  const props: LocationFormProps = {
    offerVenue: makeVenueListItem({}),
    ...params.props,
  }

  const contextValues: IndividualOfferContextValues = {
    ...individualOfferContextValuesFactory(),
    ...params.contextValues,
  }
  const options: RenderWithProvidersOptions = {
    user: sharedCurrentUserFactory(),
    ...params.options,
  }

  const Component = () => {
    const formProviderProps = useForm<LocationFormValues>({
      defaultValues: {
        address: {
          addressAutocomplete: undefined,
          banId: undefined,
          city: undefined,
          coords: undefined,
          inseeCode: undefined,
          isManualEdition: false,
          isVenueAddress: false,
          latitude: undefined,
          locationLabel: undefined,
          longitude: undefined,
          offerLocation: undefined,
          postalCode: undefined,
          'search-addressAutocomplete': undefined,
          street: undefined,
        },
        url: undefined,

        ...params.formDefaultValues,
      },
    })

    return (
      <FormProvider {...formProviderProps}>
        <LocationForm {...props} />
      </FormProvider>
    )
  }

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValues}>
      <Component />
    </IndividualOfferContext.Provider>,
    options
  )
}

describe('<LocationForm />', () => {
  const contextValuesBase: Partial<IndividualOfferContextValues> = {
    subCategories: MOCKED_SUBCATEGORIES,
  }
  const options: RenderWithProvidersOptions = {
    features: ['WIP_ENABLE_NEW_OFFER_CREATION_FLOW'],
  }

  it('should render (without accessibility violations)', async () => {
    const { container } = renderLocationForm({})

    expect(
      screen.getByRole('heading', {
        name: LABELS.sectionTitles.location,
      })
    ).toBeInTheDocument()

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should NOT display offer location subform when offer subcategory is online', () => {
    renderLocationForm({
      contextValues: {
        ...contextValuesBase,
        offer: getIndividualOfferFactory({
          subcategoryId: MOCKED_SUBCATEGORY.NON_EVENT_ONLINE.id,
        }),
      },
    })

    expect(
      screen.queryByRole('group', {
        name: LABELS.fields.offerLocation,
      })
    ).not.toBeInTheDocument()
  })

  it('should display url field when offer subcategory is online', () => {
    const contextValues: Partial<IndividualOfferContextValues> = {
      ...contextValuesBase,
      offer: getIndividualOfferFactory({
        subcategoryId: MOCKED_SUBCATEGORY.EVENT_ONLINE.id,
      }),
    }

    renderLocationForm({ contextValues, options })

    expect(
      screen.getByRole('heading', {
        name: LABELS.sectionTitles.location,
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('textbox', {
        name: LABELS.fields.url,
      })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('radiogroup', {
        name: LABELS.fields.offerLocation,
      })
    ).not.toBeInTheDocument()
  })

  it('should display location field when offer subcategory is offline', () => {
    const contextValues: Partial<IndividualOfferContextValues> = {
      ...contextValuesBase,
      offer: getIndividualOfferFactory({
        subcategoryId: MOCKED_SUBCATEGORY.EVENT_OFFLINE.id,
      }),
    }

    renderLocationForm({ contextValues, options })

    expect(
      screen.getByRole('heading', {
        name: LABELS.sectionTitles.location,
      })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('radiogroup', {
        name: LABELS.fields.offerLocation,
      })
    ).toBeInTheDocument()

    expect(
      screen.queryByRole('textbox', {
        name: LABELS.fields.url,
      })
    ).not.toBeInTheDocument()
  })
})
