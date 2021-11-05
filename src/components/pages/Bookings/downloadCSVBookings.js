import * as pcapi from 'repository/pcapi/pcapi'
import { API_URL } from 'utils/config'

export const downLoadCSVFile = async queryParams => {
  const url = new URL(`${API_URL}/bookings/csv`)
  const params = pcapi.buildFetchParams(queryParams)
  Object.keys(params).forEach(key => url.searchParams.append(key, params[key]))

  try {
    const result = await fetch(url, { credentials: 'include' })

    if (result.status === 200) {
      const text = await result.text()
      const fakeLink = document.createElement('a')
      const blob = new Blob([text], { type: "text/csv" })
      const date = new Date().toISOString()
      fakeLink.href = URL.createObjectURL(blob)
      fakeLink.setAttribute('download', `reservations_pass_culture-${date}.csv`)
      document.body.appendChild(fakeLink)
      fakeLink.click()
      document.body.removeChild(fakeLink)

      return 'success'
    }

    return 'error'
  } catch (e) {
    return 'error'
  }
}
