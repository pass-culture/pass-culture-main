import { validationSchema as ticketWithdrawalValidationSchema } from './TicketWithdrawal'
import { validationSchema as venueValidationSchema } from './Venue'

const validationSchema = {
  ...venueValidationSchema,
  ...ticketWithdrawalValidationSchema,
}

export default validationSchema
