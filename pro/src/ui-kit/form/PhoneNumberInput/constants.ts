import type { CountryCode } from 'libphonenumber-js'

export const PHONE_CODE_COUNTRY_CODE_OPTIONS: {
  label: string
  value: CountryCode
}[] = [
  { label: '+33', value: 'FR' },
  { label: '+262', value: 'YT' },
  { label: '+508', value: 'PM' },
  { label: '+590', value: 'GP' },
  { label: '+594', value: 'GF' },
  { label: '+596', value: 'MQ' },
  { label: '+687', value: 'NC' },
]

export const PLACEHOLDER_MAP: Partial<Record<CountryCode, string>> = {
  FR: '06 39 98 01 01',
  YT: '06 92 12 34 56',
  PM: '055 12 34',
  GP: '06 90 00 12 34',
  GF: '06 94 20 12 34',
  MQ: '06 90 20 12 34',
  NC: '75 12 34',
}
