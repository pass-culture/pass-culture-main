import fetch from 'node-fetch'

import { API_URL } from '../../src/utils/config'

export async function fetchFeatures() {
  const path = `${API_URL}/features`
  const result = await fetch(path, {
    headers: {
      'Content-Type': 'application/json',
      Origin: 'http://localhost:3001',
    },
  })

  const features = await result.json()

  return features
}
