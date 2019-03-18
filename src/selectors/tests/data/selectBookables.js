export const stockWithoutEventOccurrence = {
  "available": 10,
  "price": 25.00,
  "bookingLimitDatetime": null,
  "eventOccurrenceId": null,
  "id": "C3LA",
  "isSoftDeleted": false,
  "modelName": "Stock",
  "offerId": "ATRQ",
};

export const stockWithEventOccurrence = {
  "available": 10,
  "bookingLimitDatetime": "2019-04-18T18:30:00Z",
  "eventOccurrence": {
    "beginningDatetime": "2019-04-19T18:30:00Z",
    "endDatetime": "2019-04-20T20:00:00Z",
    "id": "KU7A",
    "isSoftDeleted": false,
    "modelName": "EventOccurrence",
    "offerId": "BYAQ",
    "type": null
  },
  "eventOccurrenceId": "KU7A",
  "id": "E4ZA",
  "isSoftDeleted": false,
  "modelName": "Stock",
  "offerId": null,
  "price": 15.00
}

export const stockWithDates = {
  "available": 10,
  "price": 25.00,
  "beginningDatetime": "2019-04-19T18:30:00Z",
  "endDatetime": "2019-04-20T20:00:00Z",
  "bookingLimitDatetime": null,
  "id": "C3LA",
  "isSoftDeleted": false,
  "modelName": "Stock",
  "offerId": "BYAQ",
}

export const stockWithoutDates = {
  "available": 10,
  "price": 25.00,
  "beginningDatetime": null,
  "endDatetime": null,
  "bookingLimitDatetime": null,
  "id": "C3LA",
  "isSoftDeleted": false,
  "modelName": "Stock",
  "offerId": "ATRQ",
}
