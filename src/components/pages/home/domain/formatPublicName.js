
export const formatPublicName = (publicName = '') => {
  const SPACE_CHARACTER = " "
  const PUBLIC_NAME_MAX_CHARACTERS = 15

  return publicName.includes(SPACE_CHARACTER) && publicName.length > PUBLIC_NAME_MAX_CHARACTERS ?
    publicName.split(SPACE_CHARACTER)[0]
    : publicName
}
