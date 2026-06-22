import { screen } from '@testing-library/dom'
import userEvent, { type UserEvent } from '@testing-library/user-event'
import { endOfDay } from 'date-fns'

import { api } from '@/apiClient/api'
import {
  CollectiveOfferAllowedAction,
  CollectiveOfferTemplateAllowedAction,
  EacFormat,
  type GetVenueResponseModel,
} from '@/apiClient/v1'
import {
  Mode,
  type OfferEducationalFormValues,
} from '@/commons/core/OfferEducational/types'
import { buildStudentLevelsMapWithDefaultValue } from '@/commons/core/OfferEducational/utils/buildStudentLevelsMapWithDefaultValue'
import {
  defaultGetVenue,
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { userOffererFactory } from '@/commons/utils/factories/userOfferersFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  OfferEducational,
  type OfferEducationalProps,
} from '../OfferEducational'

vi.mock('@/apiClient/api', () => ({
  api: {
    createCollectiveOffer: vi.fn(),
    createCollectiveOfferTemplate: vi.fn(),
    editCollectiveOffer: vi.fn(),
    editCollectiveOfferTemplate: vi.fn(),
  },
}))

function renderOfferEducational(
  {
    mode,
    offer,
    isTemplate,
  }: Pick<OfferEducationalProps, 'mode' | 'isTemplate' | 'offer'>,
  customVenue?: Partial<GetVenueResponseModel>,
  features?: string[]
) {
  const domainsOptions = [
    {
      id: '1',
      label: 'domain1',
      nationalPrograms: [{ id: 1, name: 'nationalProgram1' }],
    },
  ]
  return renderWithProviders(
    <OfferEducational
      userOfferer={userOffererFactory()}
      domainsOptions={domainsOptions}
      isTemplate={isTemplate}
      mode={mode}
      offer={offer}
    />,
    {
      storeOverrides: {
        user: { selectedPartnerVenue: { ...defaultGetVenue, ...customVenue } },
      },
      features,
    }
  )
}

async function fillForm(
  user: UserEvent,
  values: Partial<OfferEducationalFormValues>
) {
  if (values.domains) {
    await user.click(screen.getByLabelText(/Domaines artistiques/))
    await user.click(screen.getByText(values.domains[0]))
  }
  if (values.formats) {
    await user.click(screen.getByLabelText(/Formats/))
    await user.click(screen.getByRole('checkbox', { name: values.formats[0] }))
  }
  if (values.title) {
    await user.clear(screen.getByLabelText(/Titre de l’offre/))
    await user.type(screen.getByLabelText(/Titre de l’offre/), values.title)
  }
  if (values.description) {
    const descriptionInput = screen.getByLabelText(
      /Décrivez ici votre projet et son interêt pédagogique/
    )
    await user.clear(descriptionInput)
    await user.type(descriptionInput, values.description)
  }
  if (values.participants) {
    await user.click(screen.getByRole('checkbox', { name: 'Collège' }))
  }
  if (values.contactOptions) {
    await user.click(
      screen.getByRole('checkbox', { name: 'Via un formulaire' })
    )
  }
  if (values.contactEmail) {
    const emailInput = screen.getByLabelText('Email*')
    await user.clear(emailInput)
    await user.type(emailInput, values.contactEmail)
  }
  if (values.bookingEmails) {
    const bookingEmailInput = screen.getByLabelText(
      'Email auquel envoyer les notifications*'
    )
    await user.clear(bookingEmailInput)
    await user.type(bookingEmailInput, values.bookingEmails[0].email)
  }
}

describe('OfferEducational > submission', () => {
  describe('CollectiveOffer', () => {
    const baseFormValues = {
      domains: ['domain1'],
      formats: [EacFormat.CONCERT],
      title: 'Test Title',
      description: 'Test Description',
      participants: buildStudentLevelsMapWithDefaultValue(false),
    }

    const baseBodyPayload = {
      audioDisabilityCompliant: false,
      description: 'Test Description',
      domains: [1],
      durationMinutes: undefined,
      formats: ['Concert'],
      interventionArea: [],
      location: {
        location: {
          isVenueLocation: true,
        },
        locationType: 'ADDRESS',
      },
      mentalDisabilityCompliant: true,
      motorDisabilityCompliant: false,
      name: 'Test Title',
      nationalProgramId: null,
      students: [
        'Collège - 6e',
        'Collège - 5e',
        'Collège - 4e',
        'Collège - 3e',
      ],
      templateId: undefined,
      venueId: 1,
      visualDisabilityCompliant: true,
    }

    it('should call createCollectiveOffer with all fields on offer creation', async () => {
      const user = userEvent.setup()
      renderOfferEducational({ mode: Mode.CREATION, isTemplate: false })

      await fillForm(user, {
        ...baseFormValues,
        contactEmail: 'test@venue.com',
        bookingEmails: [{ email: 'booking@venue.com' }],
      })
      await user.click(screen.getByRole('button', { name: /Enregistrer/ }))

      expect(api.createCollectiveOffer).toHaveBeenCalledExactlyOnceWith({
        body: {
          ...baseBodyPayload,
          bookingEmails: ['booking@venue.com'],
          contactEmail: 'test@venue.com',
          contactPhone: '',
        },
      })
    })

    it('should take email and phone defaults from the venue', async () => {
      const user = userEvent.setup()
      renderOfferEducational(
        { mode: Mode.CREATION, isTemplate: false },
        {
          collectiveEmail: 'contact@venue.com',
          collectivePhone: '+33100000000',
        }
      )

      await fillForm(user, baseFormValues)
      await user.click(screen.getByRole('button', { name: /Enregistrer/ }))

      expect(api.createCollectiveOffer).toHaveBeenCalledExactlyOnceWith({
        body: {
          ...baseBodyPayload,
          bookingEmails: ['contact@venue.com'],
          contactEmail: 'contact@venue.com',
          contactPhone: '+33100000000',
        },
      })
    })

    it('should not send contactEmail, bookingEmails and contactPhone when WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS is enabled', async () => {
      const user = userEvent.setup()
      renderOfferEducational(
        { mode: Mode.CREATION, isTemplate: false },
        { collectiveEmail: 'test@venue.com', collectivePhone: '+33100000000' },
        ['WIP_ENABLE_NEW_COLLECTIVE_PRICE_DETAILS']
      )

      await fillForm(user, baseFormValues)
      await user.click(screen.getByRole('button', { name: /Enregistrer/ }))

      expect(api.createCollectiveOffer).toHaveBeenCalledExactlyOnceWith({
        body: baseBodyPayload,
      })
    })

    it('should call editCollectiveOffer with all fields on offer edition', async () => {
      const user = userEvent.setup()
      const offer = getCollectiveOfferFactory({
        allowedActions: [CollectiveOfferAllowedAction.CAN_EDIT_DETAILS],
      })
      renderOfferEducational({ mode: Mode.EDITION, offer, isTemplate: false })

      await fillForm(user, { title: 'Mon nouveau titre' })
      await user.click(screen.getByRole('button', { name: /Enregistrer/ }))

      expect(api.editCollectiveOffer).toHaveBeenCalledExactlyOnceWith({
        body: { name: 'Mon nouveau titre' },
        path: { offer_id: offer.id },
      })
    })
  })

  describe('CollectiveOfferTemplate', () => {
    it('should call createCollectiveOfferTemplate with all fields on offer creation', async () => {
      const user = userEvent.setup()
      renderOfferEducational({ mode: Mode.CREATION, isTemplate: true })

      await fillForm(user, {
        domains: ['domain1'],
        formats: [EacFormat.CONCERT],
        title: 'Test Title',
        description: 'Test Description',
        contactOptions: { form: true, email: false, phone: false },
        bookingEmails: [{ email: 'booking@venue.com' }],
        participants: buildStudentLevelsMapWithDefaultValue(false),
      })
      await user.click(screen.getByRole('button', { name: /Enregistrer/ }))

      expect(api.createCollectiveOfferTemplate).toHaveBeenCalledExactlyOnceWith(
        {
          body: {
            audioDisabilityCompliant: false,
            bookingEmails: ['booking@venue.com'],
            contactEmail: undefined,
            contactForm: 'form',
            contactPhone: undefined,
            contactUrl: undefined,
            dates: undefined,
            description: 'Test Description',
            domains: [1],
            durationMinutes: undefined,
            formats: ['Concert'],
            interventionArea: [],
            location: {
              location: { isVenueLocation: true },
              locationType: 'ADDRESS',
            },
            mentalDisabilityCompliant: true,
            motorDisabilityCompliant: false,
            name: 'Test Title',
            nationalProgramId: null,
            priceDetail: '',
            students: [
              'Collège - 6e',
              'Collège - 5e',
              'Collège - 4e',
              'Collège - 3e',
            ],
            venueId: 1,
            visualDisabilityCompliant: true,
          },
        }
      )
    })

    it('should call editCollectiveOfferTemplate with all fields on offer edition', async () => {
      const user = userEvent.setup()
      const start = new Date().toISOString().replace(/\d{2}\.\d{3}Z$/, '00Z')
      const end = endOfDay(new Date())
        .toISOString()
        .replace(/\d{2}\.\d{3}Z$/, '00Z')
      const offer = getCollectiveOfferTemplateFactory({
        allowedActions: [CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS],
        dates: { start, end },
      })
      renderOfferEducational({ mode: Mode.EDITION, offer, isTemplate: true })

      await fillForm(user, { title: 'My new template title' })
      await user.click(screen.getByRole('button', { name: /Enregistrer/ }))

      expect(api.editCollectiveOfferTemplate).toHaveBeenCalledExactlyOnceWith({
        body: {
          contactEmail: 'toto@example.com',
          contactForm: null,
          contactPhone: '0600000000',
          contactUrl: null,
          dates: { start, end },
          name: 'My new template title',
        },
        path: { offer_id: offer.id },
      })
    })
  })
})
