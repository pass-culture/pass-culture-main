import * as pcapi from 'repository/pcapi/pcapi'


export const downloadCSVFile = async filters => {
  try {
    const bookingsCsvText = await pcapi.getFilteredBookingsCSV(filters)

    const fakeLink = document.createElement('a')
    const blob = new Blob([bookingsCsvText], { type: "text/csv" })
    const date = new Date().toISOString()
    fakeLink.href = URL.createObjectURL(blob)
    fakeLink.setAttribute('download', `reservations_pass_culture-${date}.csv`)
    document.body.appendChild(fakeLink)
    fakeLink.click()
    document.body.removeChild(fakeLink)
    return Promise.resolve('success')
  } catch (e) {
    return Promise.reject('error')
  }
}
