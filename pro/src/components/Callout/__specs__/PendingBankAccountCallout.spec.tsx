import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import PendingBankAccountCallout, {
  PendingBankAccountCalloutProps,
} from 'components/Callout/PendingBankAccountCallout'
import * as useAnalytics from 'hooks/useAnalytics'
import { defaultGetOffererResponseModel } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

describe('PendingBankAccountCallout', () => {
  const props: PendingBankAccountCalloutProps = {
    titleOnly: false,
  }
  it('should not render PendingBankAccountCallout without FF', () => {
    renderWithProviders(<PendingBankAccountCallout {...props} />)

    expect(
      screen.queryByText(
        /Compte bancaire en cours de validation par nos services/
      )
    ).not.toBeInTheDocument()
    expect(
      screen.queryByRole('link', {
        name: 'Suivre mon dossier de compte bancaire',
      })
    ).not.toBeInTheDocument()
  })

  describe('With FF enabled', () => {
    it('should not render the pending bank account banner if the offerer has no pending bank account', () => {
      props.offerer = {
        ...defaultGetOffererResponseModel,
        hasPendingBankAccount: false,
      }
      renderWithProviders(<PendingBankAccountCallout {...props} />, {
        features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
      })

      expect(
        screen.queryByText(
          /Compte bancaire en cours de validation par nos services/
        )
      ).not.toBeInTheDocument()
    })

    it('should render PendingBankAccountCallout if the offerer has a pending bank account', () => {
      props.offerer = {
        ...defaultGetOffererResponseModel,
        hasPendingBankAccount: true,
      }
      renderWithProviders(<PendingBankAccountCallout {...props} />, {
        features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'],
      })

      expect(
        screen.getByText(
          /Compte bancaire en cours de validation par nos services/
        )
      ).toBeInTheDocument()
      expect(
        screen.getByRole('link', {
          name: 'Suivre mon dossier de compte bancaire',
        })
      ).toBeInTheDocument()
    })

    it('should log  pending bank account click on when callout link is clicked', async () => {
      const mockLogEvent = vi.fn()
      vi.spyOn(useAnalytics, 'default').mockImplementation(() => ({
        logEvent: mockLogEvent,
      }))
      renderWithProviders(
        <PendingBankAccountCallout
          titleOnly={props.titleOnly}
          offerer={{
            ...defaultGetOffererResponseModel,
            id: 123,
            hasPendingBankAccount: true,
          }}
        />,
        { features: ['WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY'] }
      )
      await userEvent.click(
        screen.getByRole('link', {
          name: 'Suivre mon dossier de compte bancaire',
        })
      )

      expect(mockLogEvent).toHaveBeenCalledWith(
        'HasClickedBankDetailsRecordFollowUp',
        {
          from: '/',
          offererId: 123,
        }
      )
    })
  })
})
