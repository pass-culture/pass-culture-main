const STEP_ID_INVOICES = 'justificatifs'
const STEP_ID_DETAILS = 'details'
const STEP_ID_BANK_INFORMATIONS = 'informations-bancaires'

// TODO: Remove after WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY deleted
export const OLD_STEP_NAMES = [STEP_ID_INVOICES, STEP_ID_DETAILS]

export const STEP_NAMES = [
  STEP_ID_INVOICES,
  STEP_ID_DETAILS,
  STEP_ID_BANK_INFORMATIONS,
]

// TODO: Remove after WIP_ENABLE_NEW_BANK_DETAILS_JOURNEY deleted
export const OLD_STEP_LIST = [
  {
    id: STEP_ID_INVOICES,
    label: 'Justificatifs de remboursement',
    url: '/remboursements/justificatifs',
  },
  {
    id: STEP_ID_DETAILS,
    label: 'Détails des remboursements',
    url: '/remboursements/details',
  },
]

export const STEP_LIST = [
  {
    id: STEP_ID_INVOICES,
    label: 'Justificatifs',
    url: '/remboursements/justificatifs',
  },
  {
    id: STEP_ID_DETAILS,
    label: 'Détails',
    url: '/remboursements/details',
  },
  {
    id: STEP_ID_BANK_INFORMATIONS,
    label: 'Informations bancaires',
    url: '/remboursements/informations-bancaires',
  },
]
