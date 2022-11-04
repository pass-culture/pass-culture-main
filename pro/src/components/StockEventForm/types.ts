import { IStockThingFormValues } from 'components/StockThingForm'

export interface IStockEventFormValues extends IStockThingFormValues {
  beginningDate: Date | '' | null
  beginningTime: Date | '' | null
}
