import { screen, waitFor } from '@testing-library/react'
import { Formik } from 'formik'

import { DEFAULT_EAC_FORM_VALUES } from 'core/OfferEducational/constants'
import { OfferEducationalFormValues, Mode } from 'core/OfferEducational/types'
import { userOffererFactory } from 'screens/OfferEducational/__tests-utils__/userOfferersFactory'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import {
  OfferEducationalForm,
  OfferEducationalFormProps,
} from '../OfferEducationalForm'

const renderOfferEducationalForm = (
  props: OfferEducationalFormProps,
  options?: RenderWithProvidersOptions,
  initialValues?: Partial<OfferEducationalFormValues>
) => {
  renderWithProviders(
    <Formik
      initialValues={{
        ...DEFAULT_EAC_FORM_VALUES,
        venueId: '1',
        offererId: '1',
        ...initialValues,
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
  isSubmitting: false,
}

describe('OfferEducationalForm', () => {
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
        screen.queryByRole('heading', { name: 'Prix' })
      ).not.toBeInTheDocument()
    })
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
        screen.queryByRole('heading', { name: 'Date et heure' })
      ).not.toBeInTheDocument()
    })
  })

  it('should show the custom form section', async () => {
    renderOfferEducationalForm({
      ...defaultProps,
      isTemplate: true,
    })

    expect(await screen.findByRole('checkbox', { name: 'Par email' }))
    expect(await screen.findByRole('checkbox', { name: 'Par téléphone' }))
    expect(await screen.findByRole('checkbox', { name: 'Via un formulaire' }))
  })

  it('should have no custom contact checked initially', async () => {
    renderOfferEducationalForm({ ...defaultProps, isTemplate: true })

    expect(
      await screen.findByRole('checkbox', { name: 'Par email' })
    ).not.toBeChecked()
    expect(
      await screen.findByRole('checkbox', { name: 'Par téléphone' })
    ).not.toBeChecked()
    expect(
      await screen.findByRole('checkbox', { name: 'Via un formulaire' })
    ).not.toBeChecked()
  })

  it('should disable save button when access is read only', async () => {
    renderOfferEducationalForm({
      ...defaultProps,
      mode: Mode.READ_ONLY,
    })

    const saveButton = await screen.findByText('Enregistrer et continuer')
    expect(saveButton).toBeDisabled()
  })

  it('should display unsaved information in the action bar when the value is not the default value', async () => {
    renderOfferEducationalForm(defaultProps)

    expect(screen.getByText('Brouillon non enregistré')).toBeInTheDocument()

    expect(
      await screen.findByRole('button', { name: 'Enregistrer et continuer' })
    ).toBeInTheDocument()
  })
})
