import get from 'lodash.get'
import { call, put, takeEvery } from 'redux-saga/effects'

import { assignErrors } from '../reducers/errors'
import { mergeFormData } from '../reducers/form'
import { capitalize } from '../utils/string'

const SIRET = 'siret'
const SIREN = 'siren'

const fromWatchSirenInput = sireType => function*(action) {
  const {
    values,
  } = action

  try {
    const response = yield call(fetch, `https://sirene.entreprise.api.gouv.fr/v1/${sireType}/${values[sireType]}`)
    if (response.status === 404)  {
      yield put(assignErrors({[sireType]: [`${capitalize(sireType)} invalide`]}))
      yield put(mergeFormData(action.name,
        {
          address: null,
          city: null,
          latitude: null,
          longitude: null,
          name: null,
          postalCode: null,
          [sireType]: null
        }
      ))
    } else {
      const body = yield call([response, 'json'])
      const dataPath = sireType === SIREN ? 'siege_social' : 'etablissement'
      yield put(mergeFormData(action.name, {
        address: get(body, `${dataPath}.l4_normalisee`),
        // geo_adresse has postal code and city name which don't belong to this field
        // address: get(body, `${dataPath}.geo_adresse`),
        city: get(body, `${dataPath}.libelle_commune`),
        latitude: parseFloat(get(body, `${dataPath}.latitude`)) || null,
        longitude: parseFloat(get(body, `${dataPath}.longitude`)) || null,
        name: get(body, `${dataPath}.l1_normalisee`) ||  get(body, `${dataPath}.l1_declaree`) || '',
        postalCode: get(body, `${dataPath}.code_postal`),
        [sireType]: get(body, `${dataPath}.${sireType}`),
      }, {
        calledFromSaga: true, // Prevent infinite loop
      }))
    }
  } catch(e) {
    console.error(e)
    yield put(assignErrors({[sireType]: [`Impossible de vérifier le ${capitalize(sireType)} saisi.`]}))
  }
}

export function* watchFormActions() {
  yield takeEvery(
    ({ type, values, options }) => {
      const result = type === 'MERGE_FORM_DATA' && !get(options, 'calledFromSaga') && get(values, `${SIREN}.length`) === 9
      return result
    },
    fromWatchSirenInput(SIREN)
  )
  yield takeEvery(
    ({ type, values, options }) => {
      return type === 'MERGE_FORM_DATA' && !get(options, 'calledFromSaga') && get(values, `${SIRET}.length`) === 14
    },
    fromWatchSirenInput(SIRET)
  )
}
