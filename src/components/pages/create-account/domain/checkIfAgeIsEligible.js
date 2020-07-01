import { getOffset } from '../utils/getOffset'

export const ELIGIBLE = 'eligible'
export const TOO_OLD = 'tooOld'
export const TOO_YOUNG = 'tooYoung'
export const SOON = 'soon'

export const checkIfAgeIsEligible = formattedBirthDate => {
  const [birthDay, birthMonth, birthYear] = formattedBirthDate.split('/')
  const birthYearInteger = parseInt(birthYear)
  const offset = getOffset()

  const seventeenthBirthdayTimestamp = new Date(
    `${birthYearInteger + 17}-${birthMonth}-${birthDay}T00:00:00${offset}`
  ).getTime()

  const eighteenthBirthdayTimestamp = new Date(
    `${birthYearInteger + 18}-${birthMonth}-${birthDay}T00:00:00${offset}`
  ).getTime()

  const nineteenthBirthdayTimestamp = new Date(
    `${birthYearInteger + 19}-${birthMonth}-${birthDay}T00:00:00${offset}`
  ).getTime()

  const currentTimestamp = Date.now()

  const isUserBetween18And19YearsOld =
    currentTimestamp >= eighteenthBirthdayTimestamp &&
    currentTimestamp < nineteenthBirthdayTimestamp
  const isUserOlderThan19YearsOld = currentTimestamp >= nineteenthBirthdayTimestamp
  const isUserYoungerThan17YearsOld = currentTimestamp < seventeenthBirthdayTimestamp
  const isUserBetween17And18YearsOld =
    currentTimestamp < eighteenthBirthdayTimestamp &&
    currentTimestamp >= seventeenthBirthdayTimestamp

  if (isUserBetween18And19YearsOld) {
    return ELIGIBLE
  }
  if (isUserOlderThan19YearsOld) {
    return TOO_OLD
  }
  if (isUserBetween17And18YearsOld) {
    return SOON
  }
  if (isUserYoungerThan17YearsOld) {
    return TOO_YOUNG
  }
}
