import { screen, waitFor } from '@testing-library/react'

import { api } from '@/apiClient/api'
import { Mode } from '@/commons/core/OfferEducational/types'
import {
  getCollectiveOfferFactory,
  getCollectiveOfferVenueFactory,
} from '@/commons/utils/factories/collectiveApiFactories'
import { venueListItemFactory } from '@/commons/utils/factories/individualApiFactories'
import {
  managedVenueFactory,
  userOffererFactory,
} from '@/commons/utils/factories/userOfferersFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { defaultEditionProps } from '../__tests-utils__/defaultProps'
import {
  OfferEducational,
  type OfferEducationalProps,
} from '../OfferEducational'

describe('screens | OfferEducational: edition', () => {
  let props: OfferEducationalProps

  beforeEach(() => {
    vi.spyOn(api, 'getVenues').mockResolvedValue({
      venues: [venueListItemFactory()],
    })

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
    renderWithProviders(<OfferEducational {...props} />)
    await screen.findByLabelText(/Structure/)

    const inputs = [
      screen.getByLabelText(`Formats`),
      screen.getByLabelText(/Titre de l’offre/),
      screen.getByLabelText('Indiquez la durée de l’évènement', {
        exact: false,
      }),
      screen.getByLabelText(/Structure/),
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
})
