import { screen, waitFor } from '@testing-library/react'
import React from 'react'

import { Mode } from 'core/OfferEducational/types'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferVenueFactory,
} from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { defaultEditionProps } from '../__tests-utils__/defaultProps'
import {
  managedVenueFactory,
  userOffererFactory,
} from '../__tests-utils__/userOfferersFactory'
import {
  DURATION_LABEL,
  EMAIL_LABEL,
  INTERVENTION_AREA_LABEL,
  NOTIFICATIONS_EMAIL_LABEL,
  OFFERER_LABEL,
  TITLE_LABEL,
  VENUE_LABEL,
} from '../constants/labels'
import { OfferEducational, OfferEducationalProps } from '../OfferEducational'

describe('screens | OfferEducational', () => {
  let props: OfferEducationalProps

  beforeEach(() => {
    props = defaultEditionProps
  })

  it('should disable all fields when mode is READONLY', async () => {
    props.userOfferers = [
      ...props.userOfferers,
      userOffererFactory({
        managedVenues: [
          managedVenueFactory({}),
          managedVenueFactory({
            collectiveInterventionArea: ['01', '02'],
          }),
        ],
      }),
    ]
    props = {
      ...props,
      offer: getCollectiveOfferFactory({
        venue: getCollectiveOfferVenueFactory(),
      }),
      mode: Mode.READ_ONLY,
    }
    renderWithProviders(<OfferEducational {...props} />)
    await screen.findByLabelText(`${VENUE_LABEL} *`)

    const inputs = [
      screen.getByLabelText(`Format *`),
      screen.getByLabelText(`${TITLE_LABEL} *`),
      screen.getByLabelText(DURATION_LABEL, { exact: false }),
      screen.getByLabelText(`${OFFERER_LABEL} *`),
      screen.getByLabelText(`${VENUE_LABEL} *`),
      screen.getByLabelText('Autre'), // one of every option
      screen.getByLabelText('Collège - 3e'), // one of every option
      screen.getByLabelText('Visuel'), // one of every option
      screen.getByLabelText('Téléphone', { exact: false }),
      screen.getByLabelText(`${EMAIL_LABEL} *`),
      screen.getByLabelText(`${NOTIFICATIONS_EMAIL_LABEL} *`),
      screen.getByLabelText(`${INTERVENTION_AREA_LABEL} *`),
    ]
    const submitButton = screen.getByRole('button', {
      name: 'Enregistrer et continuer',
    })
    await waitFor(() => {
      inputs.forEach((input) => expect(input).toBeDisabled())
    })
    expect(submitButton).toBeDisabled()
  })
})
