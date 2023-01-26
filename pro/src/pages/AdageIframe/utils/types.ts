// See attributesToRetrieve
export interface ResultType {
  objectID: string
  offer: {
    dates: number[]
    name: string
    thumbUrl: string
  }
  venue: {
    name: string
    publicName: string
  }
  isTemplate: boolean
  __queryID: string
}
