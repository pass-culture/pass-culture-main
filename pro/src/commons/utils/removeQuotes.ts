/**
 * Removes various quotes types ", “, ”, « » from a string
 *
 * @param message string
 * @returns string
 */
export const removeQuotes = (value: string): string => {
  return value.replace(/("|“|”|(« ?)|( ?»))/g, '')
}
