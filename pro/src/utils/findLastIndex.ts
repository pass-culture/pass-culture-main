export function findLastIndex<T>(
  array: Array<T>,
  predicate: (value: T) => boolean
): number {
  let l = array.length
  while (l--) {
    if (predicate(array[l])) return l
  }
  return -1
}
