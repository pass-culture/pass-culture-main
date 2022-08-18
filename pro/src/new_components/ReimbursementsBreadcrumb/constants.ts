const STEP_ID_INVOICES = 'justificatifs'
const STEP_ID_DETAILS = 'details'
export const STEP_NAMES = [STEP_ID_INVOICES, STEP_ID_DETAILS]

export const STEP_LIST = [
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
