import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import * as useAnalytics from '@/app/App/analytics/firebase'
import { BankAccountEvents } from '@/commons/core/FirebaseEvents/constants'
import { defaultGetOffererResponseModel } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  LinkVenueCallout,
  type LinkVenueCalloutProps,
} from './LinkVenueCallout'

const mockLogEvent = vi.fn()

describe('LinkVenueCallout', () => {
  let props: LinkVenueCalloutProps = {
    titleOnly: false,
  }
  it('should not render LinkVenueCallout without FF', () => {
    renderWithProviders(<LinkVenueCallout {...props} />)

    expect(
      screen.queryByText(/Dernière étape pour vous faire rembourser/)
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('link', {
        name: 'Gérer le rattachement de ma structure',
      })
    ).not.toBeInTheDocument()
  })

  describe('With FF enabled', () => {
    it.each([
      {
        ...defaultGetOffererResponseModel,
        hasValidBankAccount: true,
        venuesWithNonFreeOffersWithoutBankAccounts: [],
      },
      {
        ...defaultGetOffererResponseModel,
        id: 2,
        hasValidBankAccount: false,
        venuesWithNonFreeOffersWithoutBankAccounts: [1],
      },
    ])('should not render the add link venue banner if the offerer  hasValidBankAccount = $hasValidBankAccount and venuesWithNonFreeOffersWithoutBankAccounts = $venuesWithNonFreeOffersWithoutBankAccounts', ({
      hasValidBankAccount,
      venuesWithNonFreeOffersWithoutBankAccounts,
      ...rest
    }) => {
      props.offerer = {
        ...rest,
        hasValidBankAccount,
        venuesWithNonFreeOffersWithoutBankAccounts,
      }
      renderWithProviders(<LinkVenueCallout {...props} />)

      expect(
        screen.queryByText(/Dernière étape pour vous faire rembourser/)
      ).not.toBeInTheDocument()
    })

    it('should render LinkVenueCallout', () => {
      props.offerer = {
        ...defaultGetOffererResponseModel,
        hasValidBankAccount: true,
        venuesWithNonFreeOffersWithoutBankAccounts: [1],
      }
      renderWithProviders(<LinkVenueCallout {...props} />)

      expect(
        screen.getByText(/Rattachement bancaire requis/)
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: 'Gérer le rattachement de mes structures',
        })
      ).toBeInTheDocument()
    })

    it('should render LinkVenueCallout with singular wording', () => {
      props.titleOnly = false
      props.offerer = {
        ...defaultGetOffererResponseModel,
        hasValidBankAccount: true,
        venuesWithNonFreeOffersWithoutBankAccounts: [1],
      }
      renderWithProviders(<LinkVenueCallout {...props} />)

      expect(
        screen.getByText(/Gérer le rattachement de mes structures/)
      ).toBeInTheDocument()

      expect(
        screen.getByText(/Rattachement bancaire requis/)
      ).toBeInTheDocument()
    })

    it('should render LinkVenueCallout with singular plural', () => {
      props = {
        titleOnly: false,
      }
      props.offerer = {
        ...defaultGetOffererResponseModel,
        hasValidBankAccount: true,
        venuesWithNonFreeOffersWithoutBankAccounts: [1, 2],
      }
      renderWithProviders(<LinkVenueCallout {...props} />)

      expect(
        screen.getByText(/Rattachement bancaire requis/)
      ).toBeInTheDocument()
    })

    it('should log add venue bank to account', async () => {
      vi.spyOn(useAnalytics, 'useAnalytics').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))

      props.offerer = {
        ...defaultGetOffererResponseModel,
        hasValidBankAccount: true,
        venuesWithNonFreeOffersWithoutBankAccounts: [1],
      }

      renderWithProviders(<LinkVenueCallout {...props} />, {
        initialRouterEntries: ['/accueil'],
      })

      await userEvent.click(
        screen.getByRole('link', {
          name: 'Gérer le rattachement de mes structures',
        })
      )

      expect(mockLogEvent).toHaveBeenCalledWith(
        BankAccountEvents.CLICKED_ADD_VENUE_TO_BANK_ACCOUNT,
        {
          from: '/accueil',
          offererId: 1,
        }
      )
    })
  })
})
