export type PlusString = `+${string}`

export type PhoneCodeSelectOption = {
  value: PlusString
}

export const PHONE_CODE_COUNTRY_CODE_OPTIONS: PhoneCodeSelectOption[] = [
  { value: '+33' },
  { value: '+262' },
  { value: '+508' },
  { value: '+590' },
  { value: '+594' },
  { value: '+596' },
  { value: '+687' },
]

export const PHONE_EXAMPLE_MAP: Record<PlusString, string> = {
  '+33': '6 12 34 56 78',
  '+262': '692 12 34 56',
  '+508': '55 12 34',
  '+590': '690 00 01 02',
  '+594': '694 00 01 02',
  '+596': '696 00 01 02',
  '+687': '75 12 34',
}
