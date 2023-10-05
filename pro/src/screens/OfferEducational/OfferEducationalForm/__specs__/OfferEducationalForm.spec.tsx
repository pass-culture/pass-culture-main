import { screen } from '@testing-library/react'
import { Formik } from 'formik'

import { DEFAULT_EAC_FORM_VALUES, Mode } from 'core/OfferEducational'
import { userOffererFactory } from 'screens/OfferEducational/__tests-utils__/userOfferersFactory'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferEducationalForm from '..'
import { OfferEducationalFormProps } from '../OfferEducationalForm'

const renderOfferEducationalForm = (
  props: OfferEducationalFormProps,
  features?: { list: { isActive: true; nameKey: string }[] }
) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        isAdmin: false,
        email: 'email@example.com',
      },
    },
    features: features,
  }
  renderWithProviders(
    <Formik
      initialValues={{
        ...DEFAULT_EAC_FORM_VALUES,
        venueId: '1',
        offererId: '1',
      }}
      onSubmit={() => {}}
    >
      <OfferEducationalForm {...props} />
    </Formik>,
    { storeOverrides }
  )
}

describe('OfferEducationalForm', () => {
  const defaultProps: OfferEducationalFormProps = {
    categories: {
      educationalCategories: [],
      educationalSubCategories: [],
    },
    userOfferers: [userOffererFactory({})],
    mode: Mode.CREATION,
    domainsOptions: [],
    nationalPrograms: [],
    isTemplate: false,
    imageOffer: null,
    onImageUpload: vi.fn(),
    onImageDelete: vi.fn(),
  }
  it('should render price details if offer is template', () => {
    renderOfferEducationalForm({ ...defaultProps, isTemplate: true })
    expect(screen.getByRole('heading', { name: 'Prix' })).toBeInTheDocument()
  })
  it('should not render price details if offer is not template', () => {
    renderOfferEducationalForm({ ...defaultProps, isTemplate: false })
    expect(
      screen.queryByRole('heading', { name: 'Prix' })
    ).not.toBeInTheDocument()
  })
  it('should render dates if offer is template and dates for template ff is active', () => {
    renderOfferEducationalForm(
      {
        ...defaultProps,
        isTemplate: true,
      },
      {
        list: [{ isActive: true, nameKey: 'WIP_ENABLE_DATES_OFFER_TEMPLATE' }],
      }
    )
    expect(
      screen.getByRole('heading', { name: 'Date et heure' })
    ).toBeInTheDocument()
  })
})
