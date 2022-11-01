import '@testing-library/jest-dom'

import { screen } from '@testing-library/react'

import { Mode } from 'core/OfferEducational'
import { RootState } from 'store/reducers'

import { defaultEditionProps, renderEACOfferForm } from '../__tests-utils__'
import {
  managedVenueFactory,
  userOffererFactory,
} from '../__tests-utils__/userOfferersFactory'
import {
  CATEGORY_LABEL,
  DURATION_LABEL,
  EMAIL_LABEL,
  INTERVENTION_AREA_LABEL,
  NOTIFICATIONS_EMAIL_LABEL,
  NOTIFICATIONS_LABEL,
  OFFERER_LABEL,
  SUBCATEGORY_LABEL,
  TITLE_LABEL,
  VENUE_LABEL,
} from '../constants/labels'
import { IOfferEducationalProps } from '../OfferEducational'

describe('screens | OfferEducational', () => {
  let props: IOfferEducationalProps
  let store: Partial<RootState>

  beforeEach(() => {
    props = defaultEditionProps
    store = {
      features: {
        initialized: true,
        list: [],
      },
    }
  })

  it('should disable all fiels when mode is READONLY', async () => {
    props.userOfferers = [
      ...props.userOfferers,
      userOffererFactory({
        id: 'OFFERER_WITH_INTERVENTION_AREA',
        managedVenues: [
          managedVenueFactory({}),
          managedVenueFactory({
            id: 'VENUE_WITH_INTERVENTION_AREA',
            collectiveInterventionArea: ['01', '02'],
          }),
        ],
      }),
    ]
    props = {
      ...props,
      mode: Mode.READ_ONLY,
    }
    renderEACOfferForm(props, store)

    const inputs = [
      screen.getByLabelText(CATEGORY_LABEL),
      screen.getByLabelText(SUBCATEGORY_LABEL),
      screen.getByLabelText(TITLE_LABEL),
      screen.getByLabelText(CATEGORY_LABEL),
      screen.getByLabelText(DURATION_LABEL, { exact: false }),
      screen.getByLabelText(OFFERER_LABEL),
      screen.getByLabelText(VENUE_LABEL),
      screen.getByLabelText('Autre'), // one of every option
      screen.getByLabelText('Collège - 3e'), // one of every option
      screen.getByLabelText('Visuel'), // one of every option
      screen.getByLabelText('Téléphone'),
      screen.getByLabelText(EMAIL_LABEL),
      screen.getByLabelText(NOTIFICATIONS_LABEL),
      screen.getByLabelText(NOTIFICATIONS_EMAIL_LABEL),
      screen.getByLabelText(INTERVENTION_AREA_LABEL),
    ]
    const submitButton = await screen.getByRole('button', {
      name: 'Enregistrer',
    })

    inputs.forEach(input => expect(input).toBeDisabled())
    expect(submitButton).toBeDisabled()
  })
})
