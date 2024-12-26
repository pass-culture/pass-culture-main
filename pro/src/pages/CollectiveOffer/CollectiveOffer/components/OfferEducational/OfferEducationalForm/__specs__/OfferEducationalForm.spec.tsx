import { screen, waitFor } from '@testing-library/react'
import { Formik } from 'formik'
import { describe, expect } from 'vitest'

import { DEFAULT_EAC_FORM_VALUES } from 'commons/core/OfferEducational/constants'
import {
  Mode,
  OfferEducationalFormValues,
} from 'commons/core/OfferEducational/types'
import {
  managedVenueFactory,
  userOffererFactory,
} from 'commons/utils/factories/userOfferersFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

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
  userOfferer: userOffererFactory({
    managedVenues: [managedVenueFactory(), managedVenueFactory()],
  }),
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
      await screen.findByRole('heading', { name: 'Quand votre offre peut-elle avoir lieu ? *' })
    ).toBeInTheDocument()
  })

  it('should not show the dates section if the offer is not a template', async () => {
    renderOfferEducationalForm({ ...defaultProps, isTemplate: false })

    await waitFor(() => {
      expect(
        screen.queryByRole('heading', { name: 'Quand votre offre peut-elle avoir lieu ? *' })
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

  describe('OA feature flag', () => {
    it('should display the right wording without the OA FF', async () => {
      renderOfferEducationalForm(defaultProps)
      await waitFor(() => {
        expect(screen.getByText('Enregistrer et continuer')).toBeEnabled()
      })

      expect(
        screen.getAllByText('Sélectionner un lieu').length
      ).toBeGreaterThan(0)
      expect(
        screen.getByText(
          /Le lieu de rattachement permet d’associer votre compte/
        )
      ).toBeInTheDocument()
    })

    it('should display the right wording with the OA FF', async () => {
      renderOfferEducationalForm(defaultProps, {
        features: ['WIP_ENABLE_OFFER_ADDRESS'],
      })
      await waitFor(() => {
        expect(screen.getByText('Enregistrer et continuer')).toBeInTheDocument()
        expect(
          screen.getAllByText(/Sélectionner une structure/).length
        ).toBeGreaterThan(0)
      })

      expect(
        screen.getByText(
          /La structure de rattachement permet d’associer votre compte/
        )
      ).toBeInTheDocument()
    })
  })
})
