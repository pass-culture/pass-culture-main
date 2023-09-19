const humanizeDelay = (delay: number): string => {
  const timeInHour = delay / 60 / 60

  if (timeInHour < 1) {
    return `${timeInHour * 60} minutes`
  } else if (timeInHour == 1) {
    return `${timeInHour} heure`
  } else if (timeInHour > 48) {
    return `${timeInHour / 24} jours`
  }
  return `${timeInHour} heures`
}

export default humanizeDelay
