import moment from 'moment'
import get from 'lodash.get'

const resolvers = {
  // events: {
  //   dateModifiedAtLastProvider: moment,
  // },
  // eventOccurences: {
  //   beginningDatetime: moment,
  //   dateModifiedAtLastProvider: moment,
  //   endDatetime: moment,
  // },
  // mediations: {
  //   dateCreated: moment,
  //   dateModifiedAtLastProvider: moment,
  // },
  // occasions: {
  //   dateCreated: moment,
  //   dateModifiedAtLastProvider: moment,
  // },
  // offers: {
  //   bookingLimitDatetime: moment,
  //   dateModified: moment,
  //   dateModifiedAtLastProvider: moment,
  // },
  // offerers: {
  //   dateCreated: moment,
  //   dateModifiedAtLastProvider: moment,
  // },
  // things: {
  //   dateModifiedAtLastProvider: moment,
  // },
  // venues: {
  //   dateModifiedAtLastProvider: moment,
  // },
  // users: {
  //   dateCreated: moment,
  // }
}

export const resolveDataCollection = (collection, collectionName) => {
  return collection
    .map(item => Object.assign({}, item,
      Object.keys(get(resolvers, collectionName, {})).reduce(
        (result, key) => Object.assign(result, {[key]: get(resolvers, `${collectionName}.${key}`, v => v)}),
        {}
      )
    ))
}