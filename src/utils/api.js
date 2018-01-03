import 'fetch-everywhere'

const URL = 'http://private-96cdcb-ledoux.apiary-mock.com'

async function api (collectionName, config) {
  const result = await fetch(`${URL}/${collectionName}`)
  const json = await result.json()
  return json
}

export default api
