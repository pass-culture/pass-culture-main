import fetch from 'node-fetch'

import { API_URL } from '../../src/utils/config'

async function fetchFeatures() {
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

export const isSummaryPageActive = async () => {
  const features = await fetchFeatures()
  const summaryPageFeature = features.find(
    f => f.nameKey === 'OFFER_FORM_SUMMARY_PAGE'
  )

  return summaryPageFeature.isActive
}
