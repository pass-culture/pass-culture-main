// TODO (igabriele, 2026-01-20): We should get rid of this util (only used once in over-engineered `getSiretData`).
// biome-ignore lint/suspicious/noExplicitAny: Generic utility function.
export const memoize = <T extends (...args: any[]) => any>(func: T): T => {
  const cache: Record<string, ReturnType<T>> = {}

  return ((...args: Parameters<T>): ReturnType<T> => {
    const strKey = args.join(',')
    if (!(strKey in cache)) {
      cache[strKey] = func(...args)
    }
    return cache[strKey]
  }) as T
}
