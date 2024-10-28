import { TICKET_WITHDRAWAL_DEFAULT_VALUES } from './TicketWithdrawal/constants'
import { VENUE_DEFAULT_VALUES } from './Venue/constants'

export const USEFUL_INFORMATIONS_DEFAULT_VALUES = {
  ...VENUE_DEFAULT_VALUES,
  ...TICKET_WITHDRAWAL_DEFAULT_VALUES,
  isNational: false,
  url: '',
  bookingContact: '',
}
