import type { CountryCode } from 'libphonenumber-js'

export const PHONE_CODE_COUNTRY_CODE_OPTIONS: {
  label: string
  value: CountryCode
}[] = [
  { label: '+33', value: 'FR' },
  { label: '+262', value: 'RE' },
  { label: '+508', value: 'PM' },
  { label: '+590', value: 'GP' },
  { label: '+594', value: 'GF' },
  { label: '+596', value: 'MQ' },
  { label: '+687', value: 'NC' },
]

export const PHONE_EXAMPLE_MAP: Partial<Record<CountryCode, string>> = {
  FR: '6 12 34 56 78',
  RE: '692 12 34 56',
  PM: '55 12 34',
  GP: '690 00 01 02',
  GF: '694 00 01 02',
  MQ: '696 00 01 02',
  NC: '75 12 34',
}
