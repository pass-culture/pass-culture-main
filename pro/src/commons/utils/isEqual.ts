// Native TypeScript version of isEqual
export const isEqual = (x: any, y: any): boolean => {
  const ok = Object.keys,
    tx = typeof x,
    ty = typeof y
  if (x && y && tx === 'object' && tx === ty) {
    const xKeys = ok(x)
    const yKeys = ok(y)
    if (xKeys.length !== yKeys.length) {
      return false
    }

    return xKeys.every((key) => isEqual(x[key], y[key]))
  }
  return x === y
}
