import { MOBILE_OS } from '../utils/config'

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

export function navigationLink (lat, long) {
    //see https://stackoverflow.com/questions/9688607/how-to-open-a-mobile-devices-map-app-when-a-user-clicks-on-a-link
    if (MOBILE_OS==='ios') {
      return "maps://maps.google.com/maps?daddr=lat,long&amp;ll="+long+","+lat
    }
    else if (MOBILE_OS==='android') {
      return "http://maps.google.com/maps?daddr=lat,long&amp;ll="+long+","+lat
    }
    else {
      return "https://www.openstreetmap.org/#map=18/"+long+"/"+lat
    }
}
