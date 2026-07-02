import { CollectiveAdditionalFeeType } from '@/apiClient/adage'

export const MAX_ADDITIONAL_FEES_LENGHT = 11
export const ADDITIONAL_FEES_OPTIONS = [
  {
    label: "Hébergement de l'intervenant",
    value: CollectiveAdditionalFeeType.ACCOMMODATION,
  },
  {
    label: "Déplacement de l'intervenant",
    value: CollectiveAdditionalFeeType.TRAVEL,
  },
  {
    label: "Repas de l'intervenant",
    value: CollectiveAdditionalFeeType.MEAL,
  },
  {
    label: 'Matériel consommable',
    value: CollectiveAdditionalFeeType.CONSUMABLE_ITEMS,
  },
  {
    label: "Droits d'auteur / de diffusion",
    value: CollectiveAdditionalFeeType.COPYRIGHT,
  },
  {
    label: 'Frais de dossier / de gestion',
    value: CollectiveAdditionalFeeType.APPLICATION_FEE,
  },
  {
    label: '',
    value: CollectiveAdditionalFeeType.OTHER,
  },
]
