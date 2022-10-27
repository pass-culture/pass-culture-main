import { IStockThingFormValues } from 'new_components/StockThingForm'

export interface IStockThingEventFormValues extends IStockThingFormValues {
  eventDatetime: string
  eventDate: string
}

export interface IStockThingEventFormValuesArray {
  events: Array<IStockThingEventFormValues>
}
