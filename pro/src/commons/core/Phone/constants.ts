export type PlusString = `+${string}`

export const PC_HANDLED_PHONE_COUNTRY_CODES = [
  '+33', // France
  '+262', // La Réunion, Mayotte et Terres australes et antarctiques françaises
  '+508', // Saint-Pierre-et-Miquelon
  '+590', // Guadeloupe, Saint-Barthélemy et Saint-Martin
  '+594', // Guyane
  '+596', // Martinique
  '+687', // Nouvelle-Calédonie
  // '+681', // Wallis-et-Futuna
  // '+689', // Polynésie Française
] as const satisfies PlusString[]

export type PassCultureHandledCountryCode =
  (typeof PC_HANDLED_PHONE_COUNTRY_CODES)[number]

export const PHONE_EXAMPLE_MAP = {
  '+33': '6 12 34 56 78',
  '+262': '692 12 34 56',
  '+508': '55 12 34',
  '+590': '690 00 01 02',
  '+594': '694 00 01 02',
  '+596': '696 00 01 02',
  '+687': '75 12 34',
} satisfies Record<PassCultureHandledCountryCode, string>
