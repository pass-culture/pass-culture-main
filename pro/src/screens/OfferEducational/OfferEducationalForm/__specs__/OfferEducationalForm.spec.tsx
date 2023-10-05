import { screen } from '@testing-library/react'
import { Formik } from 'formik'

import { DEFAULT_EAC_FORM_VALUES, Mode } from 'core/OfferEducational'
import { userOffererFactory } from 'screens/OfferEducational/__tests-utils__/userOfferersFactory'
import { renderWithProviders } from 'utils/renderWithProviders'

import OfferEducationalForm from '..'
import { OfferEducationalFormProps } from '../OfferEducationalForm'

const renderOfferEducationalForm = (props: OfferEducationalFormProps) => {
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
    </Formik>
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
})
