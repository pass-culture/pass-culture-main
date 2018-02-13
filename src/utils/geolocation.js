export async function getGeolocationPosition (config = {}) {
  const geolocation = navigator.geolocation
  if (!geolocation) {
    alert("Erreur : pas de géolocalisation")
    return null
  }
  return new Promise((resolve, reject) => {
    geolocation.getCurrentPosition(
      position => resolve(position),
      error => reject(error),
      config
    )
  })
}
