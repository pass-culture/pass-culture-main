import { screen, waitFor } from '@testing-library/react'
import { Formik } from 'formik'

import { api } from 'apiClient/api'
import { DEFAULT_EAC_FORM_VALUES, Mode } from 'core/OfferEducational'
import { userOffererFactory } from 'screens/OfferEducational/__tests-utils__/userOfferersFactory'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import OfferEducationalForm from '..'
import { OfferEducationalFormProps } from '../OfferEducationalForm'

const renderOfferEducationalForm = (
  props: OfferEducationalFormProps,
  options?: RenderWithProvidersOptions
) => {
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
    options
  )
}

const defaultProps: OfferEducationalFormProps = {
  userOfferers: [userOffererFactory({})],
  mode: Mode.CREATION,
  domainsOptions: [],
  nationalPrograms: [],
  isTemplate: false,
  imageOffer: null,
  onImageUpload: vi.fn(),
  onImageDelete: vi.fn(),
}

describe('OfferEducationalForm', () => {
  beforeEach(() => {
    vi.spyOn(api, 'canOffererCreateEducationalOffer').mockResolvedValue({
      canCreate: true,
    })
  })

  it('should render price details if offer is template', async () => {
    renderOfferEducationalForm({ ...defaultProps, isTemplate: true })

    expect(
      await screen.findByRole('heading', { name: 'Prix' })
    ).toBeInTheDocument()
  })

  it('should not render price details if offer is not template', async () => {
    renderOfferEducationalForm({ ...defaultProps, isTemplate: false })

    await waitFor(() => {
      expect(
        screen.queryByText(
          /Pour proposer des offres à destination d’un groupe scolaire, vous devez renseigner un lieu pour pouvoir être remboursé./
        )
      ).not.toBeInTheDocument()
    })
    expect(
      screen.queryByRole('heading', { name: 'Prix' })
    ).not.toBeInTheDocument()
  })

  it('should show the dates section if the offer is a template', async () => {
    renderOfferEducationalForm({ ...defaultProps, isTemplate: true })
    expect(
      await screen.findByRole('heading', { name: 'Date et heure' })
    ).toBeInTheDocument()
  })

  it('should not show the dates section if the offer is not a template', async () => {
    renderOfferEducationalForm({ ...defaultProps, isTemplate: false })
    await waitFor(() => {
      expect(
        screen.queryByText(
          /Pour proposer des offres à destination d’un groupe scolaire, vous devez renseigner un lieu pour pouvoir être remboursé./
        )
      ).not.toBeInTheDocument()
    })

    expect(
      screen.queryByRole('heading', { name: 'Date et heure' })
    ).not.toBeInTheDocument()
  })
})
