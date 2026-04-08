export type SelectOption<T extends string | number | undefined = string> = {
  value: T
  label: string
  thumbUrl?: string | null
}
