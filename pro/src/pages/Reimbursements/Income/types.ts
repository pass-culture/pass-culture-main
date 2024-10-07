export type IncomeType = 'aggregatedRevenue' | 'expectedRevenue'
export type IncomeResults = {
  total: number
  individual?: number
  group?: number
}
export type IncomeByYear = Record<
  number,
  Partial<Record<IncomeType, IncomeResults>>
>
