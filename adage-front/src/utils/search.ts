export const FALSE = 0
export const TRUE = 1

// List of fields stored in AppSearch
export const AppSearchFields = {
  artist: "artist",
  category: "category",
  date_created: "date_created",
  dates: "dates",
  description: "description",
  group: "group",
  is_digital: "is_digital",
  is_duo: "is_duo",
  is_educational: "is_educational",
  is_event: "is_event",
  is_thing: "is_thing",
  label: "label",
  name: "name",
  id: "id",
  prices: "prices",
  ranking_weight: "ranking_weight",
  stocks_date_created: "stocks_date_created",
  tags: "tags",
  times: "times",
  thumb_url: "thumb_url",
  offerer_name: "offerer_name",
  venue_department_code: "venue_department_code",
  venue_id: "venue_id",
  venue_name: "venue_name",
  venue_position: "venue_position",
  venue_public_name: "venue_public_name",
}

// We don't use all the fields indexed. Simply retrieve the one we use.
export const RESULT_FIELDS = {
  [AppSearchFields.dates]: { raw: {} },
  [AppSearchFields.id]: { raw: {} },
  [AppSearchFields.name]: { raw: {} },
  [AppSearchFields.thumb_url]: { raw: {} },
  [AppSearchFields.venue_name]: { raw: {} },
  [AppSearchFields.venue_public_name]: { raw: {} },
}

export const SORT_OPTIONS = [
  { _score: "desc" },
  { [AppSearchFields.ranking_weight]: "desc" },
  { [AppSearchFields.date_created]: "asc" },
]
