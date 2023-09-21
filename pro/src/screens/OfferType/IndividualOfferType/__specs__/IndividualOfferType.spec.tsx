import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormikProvider, useFormik } from 'formik'
import React from 'react'

import { api } from 'apiClient/api'
import { VenueTypeCode } from 'apiClient/v1'
import { SubcategoryIdEnum } from 'apiClient/v1/models/SubcategoryIdEnum'
import {
  COLLECTIVE_OFFER_SUBTYPE,
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
  INDIVIDUAL_OFFER_SUBTYPE,
  OFFER_TYPES,
} from 'core/Offers/constants'
import { OfferTypeFormValues } from 'screens/OfferType/types'
import {
  individualOfferCategoryFactory,
  individualOfferSubCategoryResponseModelFactory,
  individualOfferVenueResponseModelFactory,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferTypeIndiviual from '../IndividualOfferType'

vi.mock('hooks/useRemoteConfig', () => ({
  __esModule: true,
  default: () => ({
    remoteConfig: {},
  }),
}))

vi.mock('@firebase/remote-config', () => ({
  getValue: () => ({ asBoolean: () => true }),
}))

const TestForm = (): JSX.Element => {
  const initialValues: OfferTypeFormValues = {
    offerType: OFFER_TYPES.INDIVIDUAL_OR_DUO,
    collectiveOfferSubtype: COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE,
    collectiveOfferSubtypeDuplicate:
      COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER,
    individualOfferSubtype: INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD,
    individualOfferSubcategory: '',
  }

  const formik = useFormik<OfferTypeFormValues>({
    initialValues: initialValues,
    onSubmit: vi.fn(),
  })

  return (
    <FormikProvider value={formik}>
      <OfferTypeIndiviual />
    </FormikProvider>
  )
}
const renderOfferTypeIndividual = (
  isFeatureActive: boolean,
  venueId?: string
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
    features: {
      list: [{ isActive: isFeatureActive, nameKey: 'WIP_CATEGORY_SELECTION' }],
    },
  }

  return renderWithProviders(<TestForm />, {
    storeOverrides,
    initialRouterEntries: [`/creation${venueId ? `?lieu=${venueId}` : ''}`],
  })
}

describe('OfferTypeIndividual', () => {
  beforeEach(() => {
    vi.spyOn(api, 'getCategories').mockResolvedValue({
      categories: [individualOfferCategoryFactory()],
      subcategories: [
        individualOfferSubCategoryResponseModelFactory({
          // id should match venueType in venueTypeSubcategoriesMapping
          id: SubcategoryIdEnum.SPECTACLE_REPRESENTATION,
          proLabel: 'Ma sous-catégorie préférée',
        }),
      ],
    })
    vi.spyOn(api, 'getVenue').mockResolvedValue({
      ...individualOfferVenueResponseModelFactory({
        venueTypeCode: 'OTHER' as VenueTypeCode, // cast is needed because VenueTypeCode in apiClient is defined in french, but sent by api in english
      }),
    })
  })

  it('should not display macro choices but specific subcategory when arriving on page', async () => {
    renderOfferTypeIndividual(true, '123')

    expect(
      await screen.findByText('Quelle est la catégorie de l’offre ?')
    ).toBeInTheDocument()
    expect(screen.getByText('Ma sous-catégorie préférée')).toBeInTheDocument()
    expect(screen.queryByText('Votre offre est :')).not.toBeInTheDocument()
  })

  it('should display macro choices when clicking on "Autre"', async () => {
    renderOfferTypeIndividual(true, '123')

    expect(
      await screen.findByText('Quelle est la catégorie de l’offre ?')
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText('Autre'))

    expect(screen.getByText('Ma sous-catégorie préférée')).toBeInTheDocument()
    expect(screen.getByText('Votre offre est :')).toBeInTheDocument()
  })

  it('should only display macro choices when feature as not been activated', () => {
    renderOfferTypeIndividual(false, '123')

    expect(
      screen.queryByText('Quelle est la catégorie de l’offre ?')
    ).not.toBeInTheDocument()
    expect(screen.getByText('Votre offre est :')).toBeInTheDocument()
  })

  it('should only display macro choices when there is no query venue id', () => {
    renderOfferTypeIndividual(true, undefined)

    expect(
      screen.queryByText('Quelle est la catégorie de l’offre ?')
    ).not.toBeInTheDocument()
    expect(screen.getByText('Votre offre est :')).toBeInTheDocument()
  })

  it('should only display macro choices when get venue api call fail', async () => {
    vi.spyOn(api, 'getVenue').mockRejectedValueOnce(null)

    renderOfferTypeIndividual(true, '123')

    expect(await screen.findByText('Votre offre est :')).toBeInTheDocument()
    expect(
      screen.queryByText('Quelle est la catégorie de l’offre ?')
    ).not.toBeInTheDocument()
  })

  it('should only display macro choices when get category api call fail', async () => {
    vi.spyOn(api, 'getCategories').mockRejectedValueOnce(null)

    renderOfferTypeIndividual(true, '123')

    expect(await screen.findByText('Votre offre est :')).toBeInTheDocument()
    expect(
      screen.queryByText('Quelle est la catégorie de l’offre ?')
    ).not.toBeInTheDocument()
  })
})
