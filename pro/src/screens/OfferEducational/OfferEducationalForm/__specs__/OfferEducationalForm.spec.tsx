import { screen, waitForElementToBeRemoved } from '@testing-library/react'
import { Formik } from 'formik'

import {
  OfferEducationalFormValues,
  DEFAULT_EAC_FORM_VALUES,
  Mode,
} from 'core/OfferEducational'
import { userOffererFactory } from 'screens/OfferEducational/__tests-utils__/userOfferersFactory'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import OfferEducationalForm from '..'
import { OfferEducationalFormProps } from '../OfferEducationalForm'

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

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

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
    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.queryByRole('heading', { name: 'Date et heure' })
    ).not.toBeInTheDocument()
  })

  it('should show the custom form section if the FF is enabled', async () => {
    renderOfferEducationalForm(
      {
        ...defaultProps,
        isTemplate: true,
      },
      {
        features: ['WIP_ENABLE_COLLECTIVE_CUSTOM_CONTACT'],
      }
    )

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(screen.getByRole('checkbox', { name: 'Par email' }))
    expect(screen.getByRole('checkbox', { name: 'Par téléphone' }))
    expect(screen.getByRole('checkbox', { name: 'Via un formulaire' }))
  })

  it('should have no custom contact checked initially', async () => {
    renderOfferEducationalForm(
      { ...defaultProps, isTemplate: true },
      {
        features: ['WIP_ENABLE_COLLECTIVE_CUSTOM_CONTACT'],
      }
    )

    await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))

    expect(
      screen.getByRole('checkbox', { name: 'Par email' })
    ).not.toBeChecked()
    expect(
      screen.getByRole('checkbox', { name: 'Par téléphone' })
    ).not.toBeChecked()
    expect(
      screen.getByRole('checkbox', { name: 'Via un formulaire' })
    ).not.toBeChecked()
  })
})
