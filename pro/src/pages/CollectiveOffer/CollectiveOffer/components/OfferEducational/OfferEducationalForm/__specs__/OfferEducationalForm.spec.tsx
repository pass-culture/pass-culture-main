import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'
import { describe, expect } from 'vitest'

import { CollectiveOfferTemplateAllowedAction } from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { getDefaultEducationalValues } from '@/commons/core/OfferEducational/constants'
import {
  Mode,
  type OfferEducationalFormValues,
} from '@/commons/core/OfferEducational/types'
import { getCollectiveOfferTemplateFactory } from '@/commons/utils/factories/collectiveApiFactories'
import {
  managedVenueFactory,
  userOffererFactory,
} from '@/commons/utils/factories/userOfferersFactories'
import { UploaderModeEnum } from '@/commons/utils/imageUploadTypes'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  OfferEducationalForm,
  type OfferEducationalFormProps,
} from '../OfferEducationalForm'

function renderOfferEducationalForm(
  props: OfferEducationalFormProps,
  options?: RenderWithProvidersOptions,
  initialValues?: Partial<OfferEducationalFormValues>
) {
  function OfferEducationalFormWrapper() {
    const form = useForm({
      defaultValues: {
        ...getDefaultEducationalValues(),
        venueId: '1',
        offererId: '1',
        ...initialValues,
      },
      mode: 'onTouched',
    })

    return (
      <FormProvider {...form}>
        <OfferEducationalForm {...props} />
      </FormProvider>
    )
  }

  return renderWithProviders(<OfferEducationalFormWrapper />, options)
}

const mockLogEvent = vi.fn()

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
        name: /Quand votre offre peut-elle avoir lieu ?/,
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

    expect(
      await screen.findByRole('checkbox', { name: 'Par email' })
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('checkbox', { name: 'Par téléphone' })
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('checkbox', { name: 'Via un formulaire' })
    ).toBeInTheDocument()
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

    const saveButton = await screen.findByRole('button', {
      name: /Enregistrer et continuer/,
    })
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

  it('should render FormLocation', async () => {
    renderOfferEducationalForm(defaultProps)
    expect(
      await screen.findByRole('radio', { name: 'À une adresse précise' })
    ).toBeInTheDocument()
  })

  it('should log an event when an image is uploaded (drag or selected)', async () => {
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    renderOfferEducationalForm(defaultProps)

    await waitFor(() => {
      expect(screen.getByLabelText('Importez une image')).toBeInTheDocument()
    })

    const imageInput = screen.getByLabelText('Importez une image')
    await userEvent.upload(imageInput, new File(['fake img'], 'fake_img.jpg'))

    expect(mockLogEvent).toHaveBeenCalledWith(Events.DRAG_OR_SELECTED_IMAGE, {
      imageType: UploaderModeEnum.OFFER_COLLECTIVE,
      imageCreationStage: 'add image',
    })
  })
})
