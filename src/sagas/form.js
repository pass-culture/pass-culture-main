import get from 'lodash.get'
import { capitalize, mergeErrors, mergeForm } from 'pass-culture-shared'
import { call, put, takeEvery } from 'redux-saga/effects'

const SIRET = 'siret'
const SIREN = 'siren'

const fromWatchSirenInput = sireType =>
  function*(action) {
    const { name, patch } = action
    if (!sireType) {
      yield put(
        mergeForm(name, {
          address: null,
          city: null,
          latitude: null,
          longitude: null,
          name: null,
          postalCode: null,
          sire: null,
        })
      )

      let wrongSireType =
        get(patch, `${SIRET}.length`) > 14
          ? SIRET
          : get(patch, `${SIREN}.length`) > 9
          ? SIREN
          : null
      if (wrongSireType) {
        yield put(
          mergeErrors(name, {
            [wrongSireType]: [`${capitalize(wrongSireType)} invalide`],
          })
        )
      }

      return
    }

    try {
      const response = yield call(
        fetch,
        `https://entreprise.data.gouv.fr/api/sirene/v1/${sireType}/${patch[sireType]}`
      )

      if (response.status === 404) {
        yield put(
          mergeErrors(name, {
            [sireType]: [`${capitalize(sireType)} invalide`],
          })
        )
        yield put(
          mergeForm(name, {
            address: null,
            city: null,
            latitude: null,
            longitude: null,
            name: null,
            postalCode: null,
            sire: null,
          })
        )
      } else {
        const body = yield call([response, 'json'])
        const dataPath = sireType === SIREN ? 'siege_social' : 'etablissement'
        const sire = get(body, `${dataPath}.${sireType}`)
        yield put(
          mergeForm(
            name,
            {
              address: get(body, `${dataPath}.l4_normalisee`),
              // geo_adresse has postal code and city name which don't belong to this field
              // address: get(body, `${dataPath}.geo_adresse`),
              city: get(body, `${dataPath}.libelle_commune`),
              latitude: parseFloat(get(body, `${dataPath}.latitude`)) || null,
              longitude: parseFloat(get(body, `${dataPath}.longitude`)) || null,
              name:
                get(body, `${dataPath}.l1_normalisee`) ||
                get(body, `${dataPath}.l1_declaree`) ||
                '',
              postalCode: get(body, `${dataPath}.code_postal`),
              [sireType]: sire,
              sire,
            },
            {
              calledFromSaga: true, // Prevent infinite loop
            }
          )
        )
      }
    } catch (e) {
      console.error(e)
      yield put(
        mergeErrors(name, {
          [sireType]: [`Impossible de vérifier le ${capitalize(sireType)} saisi.`],
        })
      )
    }
  }

export function* watchFormActions() {
  yield takeEvery(
    ({ type, config, patch }) =>
      /MERGE_FORM_(.*)/.test(type) &&
      get(config, 'isSagaCalling') &&
      !get(config, 'calledFromSaga') &&
      get(config, 'type') === 'siren' &&
      get(patch, `${SIREN}.length`) === 9,
    fromWatchSirenInput(SIREN)
  )
  yield takeEvery(
    ({ type, config, patch }) =>
      /MERGE_FORM_(.*)/.test(type) &&
      get(config, 'isSagaCalling') &&
      !get(config, 'calledFromSaga') &&
      get(config, 'type') === 'siret' &&
      get(patch, `${SIRET}.length`) === 14,
    fromWatchSirenInput(SIRET)
  )
  yield takeEvery(
    ({ type, config, patch }) =>
      /MERGE_FORM_(.*)/.test(type) &&
      get(config, 'isSagaCalling') &&
      !get(config, 'calledFromSaga') &&
      ((get(config, 'type') === 'siren' && get(patch, `${SIREN}.length`) !== 9) ||
        (get(config, 'type') === 'siret' && get(patch, `${SIRET}.length`) !== 14)),
    fromWatchSirenInput(null)
  )
}
