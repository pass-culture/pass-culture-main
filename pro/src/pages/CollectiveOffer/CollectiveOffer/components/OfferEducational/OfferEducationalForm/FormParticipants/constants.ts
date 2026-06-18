import { StudentLevels } from '@/apiClient/v1'

export const studentLevelsLabels = {
  [StudentLevels._COLES_MARSEILLE_MATERNELLE]: 'Maternelle',
  [StudentLevels._COLES_MARSEILLE_CP_CE1_CE2]: 'CP, CE1, CE2',
  [StudentLevels._COLES_MARSEILLE_CM1_CM2]: 'CM1, CM2',
  [StudentLevels.COLL_GE_6E]: '6e',
  [StudentLevels.COLL_GE_5E]: '5e',
  [StudentLevels.COLL_GE_4E]: '4e',
  [StudentLevels.COLL_GE_3E]: '3e',
  [StudentLevels.CAP_1RE_ANN_E]: 'CAP - 1re année',
  [StudentLevels.CAP_2E_ANN_E]: 'CAP - 2e année',
  [StudentLevels.LYC_E_SECONDE]: 'Seconde',
  [StudentLevels.LYC_E_PREMI_RE]: 'Première',
  [StudentLevels.LYC_E_TERMINALE]: 'Terminale',
}
