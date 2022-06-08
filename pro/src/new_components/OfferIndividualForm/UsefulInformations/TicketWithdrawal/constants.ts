export const TICKET_WITHDRAWAL_DEFAULT_VALUES = {
  withdrawalDetails: '',
  ticketWithdrawal: '',
  ticketSentDate: '',
  ticketWithdrawalHour: '',
}

export const TICKETWITHDRAWAL = {
  withoutTicket: 'withoutTicket',
  emailTicket: 'emailTicket',
  onPlaceTicket: 'onPlaceTicket',
}

export const ticketWithdrawalTypeRadios = [
  {
    label: 'Événement sans billet',
    value: TICKETWITHDRAWAL.withoutTicket,
  },
  {
    label: 'Envoi par e-mail',
    value: TICKETWITHDRAWAL.emailTicket,
  },
  {
    label: 'Retrait sur place (guichet, comptoir ...)',
    value: TICKETWITHDRAWAL.onPlaceTicket,
  },
]

export const ticketSentDateOptions = [
  {
    label: 'Date indéterminée',
    value: 'undeterminedDate',
  },
  {
    label: '24 heures',
    value: '24Hours',
  },
  {
    label: '48 heures',
    value: '48Hours',
  },
  {
    label: '3 jours',
    value: '3Days',
  },
  {
    label: '4 jours',
    value: '4Days',
  },
  {
    label: '5 jours',
    value: '5Days',
  },
  {
    label: '6 jours',
    value: '6Days',
  },
  {
    label: '1 semaine',
    value: '1Week',
  },
]

export const ticketWithdrawalHourOptions = [
  {
    label: 'À tout moment',
    value: 'anytime',
  },
  {
    label: '15 minutes',
    value: '15Minutes',
  },
  {
    label: '30 minutes',
    value: '30Minutes',
  },
  {
    label: '1 heure',
    value: '1Hour',
  },
  {
    label: '2 heures',
    value: '2Hours',
  },
  {
    label: '4 heures',
    value: '4Hours',
  },
  {
    label: '24 heures',
    value: '24Hours',
  },
  {
    label: '48 heures',
    value: '48Hours',
  },
]
