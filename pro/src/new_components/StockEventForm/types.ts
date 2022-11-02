import { IStockThingFormValues } from 'new_components/StockThingForm'

export interface IStockEventFormValues extends IStockThingFormValues {
  beginningDate: Date | '' | null
  beginningTime: Date | '' | null
}
