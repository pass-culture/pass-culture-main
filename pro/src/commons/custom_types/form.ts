export type SelectOption<T extends string | number = string> = {
  value: T
  label: string
  description?: string | null
  thumbUrl?: string | null
}

export type ApiOption = SelectOption & Record<string, unknown>
