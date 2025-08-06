import { screen, waitFor, within } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as hooks from '@/commons/hooks/swr/useOfferer'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import {
  currentOffererFactory,
  sharedCurrentUserFactory,
} from '@/commons/utils/factories/storeFactories'
import {
  managedVenueFactory,
  userOffererFactory,
} from '@/commons/utils/factories/userOfferersFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { defaultCreationProps } from '../__tests-utils__/defaultProps'
import { INTERVENTION_AREA_LABEL } from '../constants/labels'
import { OfferEducational, OfferEducationalProps } from '../OfferEducational'

vi.mock('@/apiClient//api', () => ({
  api: {
    getVenues: vi.fn(),
  },
}))

function renderOfferEducational(props: OfferEducationalProps) {
  const user = sharedCurrentUserFactory()
  renderWithProviders(<OfferEducational {...props} />, {
    user,
    storeOverrides: {
      user: {
        currentUser: user,
      },
      offerer: currentOffererFactory(),
    },
  })
}

describe('screens | OfferEducational : event address step', () => {
  let props: OfferEducationalProps
  const mockOffererData = {
    data: { ...defaultGetOffererResponseModel, isValidated: true },
    isLoading: false,
    error: undefined,
    mutate: vi.fn(),
    isValidating: false,
  }

  describe('when there is only one venue managed by the offerer', () => {
    beforeEach(() => {
      props = {
        ...defaultCreationProps,
      }

      vi.spyOn(hooks, 'useOfferer').mockReturnValue(mockOffererData)
    })

    it('should display venue radio buttons with pre-selected offerer venue and a disabled select', async () => {
      renderOfferEducational(props)

      await waitFor(() => {
        expect(
          screen.getByLabelText('Sélectionner la structure *')
        ).toHaveValue('1')
      })
      expect(
        screen.getByLabelText('Sélectionner la structure *')
      ).toBeDisabled()

      expect(
        await screen.findByText('Venue name', { exact: false, selector: 'div' })
      ).toBeInTheDocument()

      expect(
        screen.queryByLabelText(INTERVENTION_AREA_LABEL)
      ).not.toBeInTheDocument()
    })

    it('should display text area + intervention area multiselect when user selects "other"', async () => {
      renderOfferEducational(props)

      await userEvent.click(await screen.findByLabelText('Autre'))
      expect(screen.getByLabelText('Autre')).toBeChecked()

      expect(
        screen.queryByLabelText('Sélectionner la structure *')
      ).not.toBeInTheDocument()

      expect(
        screen.getByLabelText('Adresse de l’évènement *')
      ).toBeInTheDocument()

      expect(screen.queryByLabelText('Département(s)')).toBeInTheDocument()
    })

    it('should not display neither event venue address nor text area if user selects "school"', async () => {
      renderOfferEducational(props)

      await userEvent.click(
        await screen.findByLabelText('Dans l’établissement scolaire')
      )
      expect(
        screen.getByLabelText('Dans l’établissement scolaire')
      ).toBeChecked()

      expect(
        screen.queryByLabelText('Sélectionner la structure *')
      ).not.toBeInTheDocument()

      expect(
        screen.queryByLabelText('Adresse de l’évènement *')
      ).not.toBeInTheDocument()

      expect(screen.queryByLabelText('Département(s)')).toBeInTheDocument()
    })
  })
  // TODO: move this test, it does not belong to Address step
  describe('when there are multiple venues managed by the offerer', () => {
    const firstVenueId = '12'
    const secondVenueId = '23'
    beforeEach(() => {
      vi.spyOn(hooks, 'useOfferer').mockReturnValue(mockOffererData)

      props = {
        ...defaultCreationProps,
        userOfferer: userOffererFactory({
          id: 1,
          managedVenues: [
            managedVenueFactory({
              id: Number(firstVenueId),
            }),
            managedVenueFactory({
              id: Number(secondVenueId),
            }),
          ],
        }),
      }
    })

    it('should prefill the venue data when switching from one event adress type to offerer venue type', async () => {
      renderOfferEducational(props)

      // wait for page to be rendered
      const offererSelect = await screen.findByLabelText('Structure *')
      // select venue to open step Address
      await userEvent.selectOptions(offererSelect, [firstVenueId])

      const offerVenueSelect = await screen.findByLabelText(
        'Sélectionner la structure *'
      )
      expect(offerVenueSelect).toHaveValue(firstVenueId)

      await userEvent.click(await screen.findByLabelText('Autre'))
      expect(screen.getByLabelText('Autre')).toBeChecked()

      await userEvent.click(
        await screen.findByLabelText('Dans votre structure')
      )
      expect(screen.getByLabelText('Dans votre structure')).toBeChecked()

      expect(offerVenueSelect).toHaveValue(firstVenueId)
    })

    it('should prefill intervention field with venue intervention field when selecting venue', async () => {
      const offererId = '55'
      const venueId = '42'

      renderOfferEducational({
        ...props,
        ...{
          userOfferer: userOffererFactory({
            id: Number(offererId),
            managedVenues: [
              managedVenueFactory({}),
              managedVenueFactory({
                id: Number(venueId),
                collectiveInterventionArea: ['01', '02'],
              }),
            ],
          }),
        },
      })

      const venuesSelect = await screen.findByLabelText('Structure *')

      await userEvent.selectOptions(venuesSelect, [venueId])

      expect(screen.queryByLabelText('Structure *')).toHaveValue(venueId)

      await userEvent.click(await screen.findByLabelText('Autre'))

      expect(screen.getByLabelText('Autre')).toBeChecked()

      const interventionArea = await screen.findByLabelText('Département(s)')
      await userEvent.click(interventionArea)

      const interventionAreaContainer = screen.getByTestId('panel-scrollable')

      const checkedItems = within(interventionAreaContainer).getAllByRole(
        'checkbox',
        { checked: true }
      )
      expect(checkedItems).toHaveLength(2)
    })
  })
})
