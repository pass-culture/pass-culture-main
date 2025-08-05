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
