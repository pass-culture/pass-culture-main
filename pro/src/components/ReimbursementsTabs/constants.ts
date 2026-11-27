import { FinanceEvents } from '@/commons/core/FirebaseEvents/constants'

export const TAB_ID_INVOICES = 'justificatifs'
export const TAB_ID_BANK_INFORMATIONS = 'informations-bancaires'
export const TAB_ID_INCOMES = 'chiffre-d-affaires'
export const TAB_ID_SETTLEMENTS = 'virements'

export const TAB_NAMES = [
  TAB_ID_INVOICES,
  TAB_ID_SETTLEMENTS,
  TAB_ID_BANK_INFORMATIONS,
  TAB_ID_INCOMES,
] as const

export type TAB_NAMES = (typeof TAB_NAMES)[number]

export const EVENT_BY_TAB = {
  [TAB_ID_SETTLEMENTS]: FinanceEvents.CLICKED_SETTLEMENTS_TAB,
  [TAB_ID_INVOICES]: FinanceEvents.CLICKED_INVOICES_TAB,
  [TAB_ID_BANK_INFORMATIONS]: FinanceEvents.CLICKED_BANK_INFO_TAB,
  [TAB_ID_INCOMES]: FinanceEvents.CLICKED_REVENUE_TAB,
} as const
