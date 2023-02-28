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

export const hasProperty = <T extends string>(
  element: unknown,
  property: T
): element is Record<T, unknown> => {
  if (element === undefined || element === null) {
    return false
  }

  return Boolean(Object.prototype.hasOwnProperty.call(element, property))
}
