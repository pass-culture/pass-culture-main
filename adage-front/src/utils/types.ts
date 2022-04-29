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
}

export enum Role {
  redactor = 'redactor',
  readonly = 'readonly',
  unauthenticated = 'unauthenticated',
}
