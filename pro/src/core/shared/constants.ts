export const urlRegex = new RegExp(
  // eslint-disable-next-line no-useless-escape
  /^(?:http(s)?:\/\/)?[\w.-\.-\.@]+(?:\.[\w\.-\.@]+)+[\w\-\._~:\/?#[\]@%!\$&'\(\)\*\+,;=.]+$/,
  'i'
)

export const GET_DATA_ERROR_MESSAGE =
  'Nous avons rencontré un problème lors de la récupération des données.'
