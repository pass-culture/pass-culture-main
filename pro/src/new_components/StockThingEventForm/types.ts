import { IStockThingFormValues } from 'new_components/StockThingForm'

export interface IStockThingEventFormValues extends IStockThingFormValues {
  eventDatetime: Date | ''
  eventTime: Date | '' | null
}

export interface IStockThingEventFormValuesArray {
  events: Array<IStockThingEventFormValues>
}
