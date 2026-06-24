import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import {
  CollectiveOfferAllowedAction,
  CollectiveOfferTemplateAllowedAction,
} from '@/apiClient/v1'
import * as useAnalytics from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { Mode } from '@/commons/core/OfferEducational/types'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferTemplateFactory,
  getCollectiveOfferVenueFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import {
  managedVenueFactory,
  userOffererFactory,
} from '@/commons/utils/factories/userOfferersFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { defaultEditionProps } from '../__tests-utils__/defaultProps'
import {
  OfferEducational,
  type OfferEducationalProps,
} from '../OfferEducational'

describe('screens | OfferEducational: edition', () => {
  let props: OfferEducationalProps

  beforeEach(() => {
    props = defaultEditionProps
  })

  it('should disable all fields when mode is READONLY', async () => {
    props.userOfferer = userOffererFactory({
      managedVenues: [
        managedVenueFactory({}),
        managedVenueFactory({
          collectiveInterventionArea: ['01', '02'],
        }),
      ],
    })
    props = {
      ...props,
      offer: getCollectiveOfferFactory({
        venue: getCollectiveOfferVenueFactory(),
      }),
      mode: Mode.READ_ONLY,
    }
    renderWithProviders(<OfferEducational {...props} />, {
      storeOverrides: {
        user: {
          selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
        },
      },
    })

    const inputs = [
      screen.getByLabelText(`Formats`),
      screen.getByLabelText(/Titre de l’offre/),
      screen.getByLabelText('Indiquez la durée de l’évènement', {
        exact: false,
      }),
      screen.getByLabelText('Collège'), // one of every option
      screen.getByLabelText('Visuel'), // one of every option
      screen.getByLabelText('Téléphone', { exact: false }),
      screen.getAllByLabelText(/Email/)[0],
      screen.getByLabelText(/Email auquel envoyer les notifications/),
    ]
    const submitButton = screen.getByRole('button', {
      name: 'Enregistrer et continuer',
    })
    await waitFor(() => {
      inputs.forEach((input) => {
        expect(input).toBeDisabled()
      })
    })
    expect(submitButton).toBeDisabled()
  })

  it.each([
    {
      isTemplate: false,
      offerId: 123,
      offerFactory: getCollectiveOfferFactory,
      allowedAction: CollectiveOfferAllowedAction.CAN_EDIT_DETAILS,
      event: Events.CLICKED_COLLECTIVE_OFFER_MODIFICATION,
      testName: 'collective offer',
    },
    {
      isTemplate: true,
      offerId: 456,
      offerFactory: getCollectiveOfferTemplateFactory,
      allowedAction: CollectiveOfferTemplateAllowedAction.CAN_EDIT_DETAILS,
      event: Events.CLICKED_COLLECTIVE_TEMPLATE_OFFER_MODIFICATION,
      testName: 'collective template',
    },
  ])('should log $testName modification on submit in edition mode', async ({
    isTemplate,
    offerId,
    offerFactory,
    allowedAction,
    event,
  }) => {
    const mockLogEvent = vi.fn()
    vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
      logEvent: mockLogEvent,
    }))

    props = {
      ...props,
      mode: Mode.EDITION,
      isTemplate,
      offer: offerFactory({
        id: offerId,
        allowedActions: [allowedAction] as any,
      }),
    }
    renderWithProviders(<OfferEducational {...props} />, {
      storeOverrides: {
        user: {
          selectedPartnerVenue: makeGetVenueResponseModel({ id: 1 }),
        },
      },
    })

    const descriptionField = await screen.findByRole('textbox', {
      name: /Décrivez ici votre projet/,
    })
    await userEvent.type(descriptionField, 'X')

    await userEvent.click(
      await screen.findByRole('button', { name: 'Enregistrer et continuer' })
    )

    expect(mockLogEvent).toHaveBeenCalledWith(event, { offerId })
  })
})
