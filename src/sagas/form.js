import { call, put, select, takeEvery } from 'redux-saga/effects'

import { newMergeForm } from '../reducers/form'
import { assignErrors } from '../reducers/errors'
import { capitalize, removeWhitespaces } from '../utils/string'
import get from 'lodash.get'

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
      yield put(newMergeForm(action.name,
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
      yield put(newMergeForm(action.name, {
        address: get(body, `${dataPath}.geo_adresse`),
        city: get(body, `${dataPath}.libelle_commune`),
        latitude: get(body, `${dataPath}.latitude`),
        longitude: get(body, `${dataPath}.longitude`),
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
      const result = type === 'NEW_MERGE_FORM' && !get(options, 'calledFromSaga') && get(values, `${SIREN}.length`) === 9
      return result
    },
    fromWatchSirenInput(SIREN)
  )
  yield takeEvery(
    ({ type, values, options }) => {
      return type === 'NEW_MERGE_FORM' && !get(options, 'calledFromSaga') && get(values, `${SIRET}.length`) === 14
    },
    fromWatchSirenInput(SIRET)
  )
}
