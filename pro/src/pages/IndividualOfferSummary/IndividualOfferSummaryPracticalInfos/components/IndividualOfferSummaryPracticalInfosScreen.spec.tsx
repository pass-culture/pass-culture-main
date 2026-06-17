import { screen } from '@testing-library/react'

import { WithdrawalTypeEnum } from '@/apiClient/v1/new'
import { getIndividualOfferFactory } from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  IndividualOfferSummaryPracticalInfosScreen,
  type IndividualOfferSummaryPracticalInfosScreenProps,
} from './IndividualOfferSummaryPracticalInfosScreen'

const defaultProps = { offer: getIndividualOfferFactory() }

function renderIndividualOfferSummaryPracticalInfosScreen(
  props?: Partial<IndividualOfferSummaryPracticalInfosScreenProps>
) {
  renderWithProviders(
    <IndividualOfferSummaryPracticalInfosScreen {...defaultProps} {...props} />
  )
}

describe('IndividualOfferSummaryPracticalInfosScreen', () => {
  it('should render the practical information summary sections', () => {
    renderIndividualOfferSummaryPracticalInfosScreen()

    expect(
      screen.getByRole('heading', { name: 'Informations pratiques' })
    ).toBeInTheDocument()
    expect(
      screen.getByRole('heading', { name: 'Notification des réservations' })
    ).toBeInTheDocument()
  })

  it('should render the offer description infos', () => {
    renderIndividualOfferSummaryPracticalInfosScreen({
      offer: getIndividualOfferFactory({
        withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
        withdrawalDelay: 10,
        withdrawalDetails: 'Details for the withdrawal',
        bookingContact: 'test@contact.co',
        bookingEmail: 'test2@contact.co',
      }),
    })

    expect(screen.getByText('Details for the withdrawal')).toBeInTheDocument()
    expect(
      screen.getByText(/Précisez la façon dont vous distribuerez les billets/)
    ).toBeInTheDocument()
    expect(screen.getByText(/Heure de retrait/)).toBeInTheDocument()
    expect(screen.getByText('test@contact.co')).toBeInTheDocument()
    expect(screen.getByText('test2@contact.co')).toBeInTheDocument()
  })
})
