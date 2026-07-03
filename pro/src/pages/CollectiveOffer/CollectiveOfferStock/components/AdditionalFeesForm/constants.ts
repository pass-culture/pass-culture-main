import { CollectiveAdditionalFeeType } from '@/apiClient/adage'
import { objectEntries } from '@/commons/utils/object'

export const MAX_ADDITIONAL_FEES_LENGHT = 11
export const ADDITIONAL_FEES = {
  [CollectiveAdditionalFeeType.ACCOMMODATION]: "Hébergement de l'intervenant•e",
  [CollectiveAdditionalFeeType.TRAVEL]: "Déplacement de l'intervenant•e",
  [CollectiveAdditionalFeeType.MEAL]: "Repas de l'intervenant•e",
  [CollectiveAdditionalFeeType.CONSUMABLE_ITEMS]: 'Matériel consommable',
  [CollectiveAdditionalFeeType.COPYRIGHT]: "Droits d'auteur",
  [CollectiveAdditionalFeeType.BROADCASTING]: 'Droits de diffusion',
  [CollectiveAdditionalFeeType.APPLICATION_FEE]: 'Frais de dossier',
  [CollectiveAdditionalFeeType.MANAGEMENT_FEE]: 'Frais de gestion',
  [CollectiveAdditionalFeeType.OTHER]: '',
} as const

export const ADDITIONAL_FEES_OPTIONS = objectEntries(ADDITIONAL_FEES).map(
  ([k, v]) => ({ value: k, label: v })
)
