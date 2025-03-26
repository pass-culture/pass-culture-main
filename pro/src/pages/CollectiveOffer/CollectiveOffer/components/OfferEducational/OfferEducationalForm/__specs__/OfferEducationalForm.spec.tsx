import { screen, waitFor } from '@testing-library/react'
import { Formik } from 'formik'
import { describe, expect } from 'vitest'

import { CollectiveOfferTemplateAllowedAction } from 'apiClient/v1'
import { DEFAULT_EAC_FORM_VALUES } from 'commons/core/OfferEducational/constants'
import {
  Mode,
  OfferEducationalFormValues,
} from 'commons/core/OfferEducational/types'
import * as hooks from 'commons/hooks/swr/useOfferer'
import { getCollectiveOfferTemplateFactory } from 'commons/utils/factories/collectiveApiFactories'
import { defaultGetOffererResponseModel } from 'commons/utils/factories/individualApiFactories'
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
  isTemplate: false,
  imageOffer: null,
  onImageUpload: vi.fn(),
  onImageDelete: vi.fn(),
  isSubmitting: false,
}

describe('OfferEducationalForm', () => {
  beforeEach(() => {
    const mockOffererData = {
      data: { ...defaultGetOffererResponseModel, isValidated: true },
      isLoading: false,
      error: undefined,
      mutate: vi.fn(),
      isValidating: false,
    }

    vi.spyOn(hooks, 'useOfferer').mockReturnValue(mockOffererData)
  })

  it('should render price details if offer is template', async () => {
    renderOfferEducationalForm({ ...defaultProps, isTemplate: true })

    expect(
      await screen.findByText('Indiquez le tarif de votre offre')
    ).toBeInTheDocument()
  })

  it('should not render price details if offer is not template', async () => {
    renderOfferEducationalForm({ ...defaultProps, isTemplate: false })

    await waitFor(() => {
      expect(
        screen.queryByText('Indiquez le tarif de votre offre')
      ).not.toBeInTheDocument()
    })
  })

  it('should show the dates section if the offer is a template', async () => {
    renderOfferEducationalForm({ ...defaultProps, isTemplate: true })
    expect(
      await screen.findByRole('heading', {
        name: 'Quand votre offre peut-elle avoir lieu ? *',
      })
    ).toBeInTheDocument()
  })

  it('should not show the dates section if the offer is not a template', async () => {
    renderOfferEducationalForm({ ...defaultProps, isTemplate: false })

    await waitFor(() => {
      expect(
        screen.queryByRole('heading', {
          name: 'Quand votre offre peut-elle avoir lieu ?',
        })
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

  it('should disable save button when CAN_EDIT_DETAILS is not allowed', async () => {
    renderOfferEducationalForm({
      ...defaultProps,
      offer: {
        ...getCollectiveOfferTemplateFactory(),
        allowedActions: [],
      },
    })

    const saveButton = await screen.findByText('Enregistrer et continuer')
    expect(saveButton).toBeDisabled()
  })

  it('should not disable form fields when CAN_EDIT_DETAILS is allowed', async () => {
    renderOfferEducationalForm({
      ...defaultProps,
      isTemplate: true,
      offer: {
        ...getCollectiveOfferTemplateFactory(),
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS],
      },
    })

    expect(
      await screen.findByRole('checkbox', { name: 'Par email' })
    ).not.toBeDisabled()
  })

  it('should display unsaved information in the action bar when the value is not the default value', async () => {
    renderOfferEducationalForm(defaultProps)

    expect(screen.getByText('Brouillon non enregistré')).toBeInTheDocument()

    expect(
      await screen.findByRole('button', { name: 'Enregistrer et continuer' })
    ).toBeInTheDocument()
  })
})
