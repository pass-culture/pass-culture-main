import { IStockThingFormValues } from 'new_components/StockThingForm'

export interface IStockEventFormValues extends IStockThingFormValues {
  beginningDate: Date | ''
  beginningTime: Date | '' | null
}

export interface IStockEventFormValuesArray {
  events: Array<IStockEventFormValues>
}
