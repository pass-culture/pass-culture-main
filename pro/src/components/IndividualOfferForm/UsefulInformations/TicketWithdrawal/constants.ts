import { WithdrawalTypeEnum } from 'apiClient/v1'
import { SUBCATEGORIES_FIELDS_DEFAULT_VALUES } from 'components/IndividualOfferForm/Categories/constants'

export const TICKET_WITHDRAWAL_DEFAULT_VALUES = {
  withdrawalDetails: '',
  withdrawalType: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['withdrawalType'],
  withdrawalDelay: SUBCATEGORIES_FIELDS_DEFAULT_VALUES['withdrawalDelay'],
}

export const ticketWithdrawalTypeRadios = [
  {
    label: 'Aucun billet n’est nécessaire',
    value: WithdrawalTypeEnum.NO_TICKET,
  },
  {
    label: 'Les billets seront envoyés par email',
    value: WithdrawalTypeEnum.BY_EMAIL,
  },
  {
    label: 'Retrait sur place (guichet, comptoir...)',
    value: WithdrawalTypeEnum.ON_SITE,
  },
]

export const providedTicketWithdrawalTypeRadios = [
  ...ticketWithdrawalTypeRadios,
  {
    label: 'Les billets seront affichés dans l’application',
    value: WithdrawalTypeEnum.IN_APP,
  },
]

export const ticketSentDateOptions = [
  {
    label: '24 heures',
    value: (60 * 60 * 24).toString(),
  },
  {
    label: '48 heures',
    value: (60 * 60 * 24 * 2).toString(),
  },
  {
    label: '3 jours',
    value: (60 * 60 * 24 * 3).toString(),
  },
  {
    label: '4 jours',
    value: (60 * 60 * 24 * 4).toString(),
  },
  {
    label: '5 jours',
    value: (60 * 60 * 24 * 5).toString(),
  },
  {
    label: '6 jours',
    value: (60 * 60 * 24 * 6).toString(),
  },
  {
    label: '1 semaine',
    value: (60 * 60 * 24 * 7).toString(),
  },
]

export const ticketWithdrawalHourOptions = [
  {
    label: 'À tout moment',
    value: (0).toString(),
  },
  {
    label: '15 minutes',
    value: (60 * 15).toString(),
  },
  {
    label: '30 minutes',
    value: (60 * 30).toString(),
  },
  {
    label: '1 heure',
    value: (60 * 60).toString(),
  },
  {
    label: '2 heures',
    value: (60 * 60 * 2).toString(),
  },
  {
    label: '4 heures',
    value: (60 * 60 * 4).toString(),
  },
  {
    label: '24 heures',
    value: (60 * 60 * 24).toString(),
  },
  {
    label: '48 heures',
    value: (60 * 60 * 48).toString(),
  },
]
