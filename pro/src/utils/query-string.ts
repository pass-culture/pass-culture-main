export const parse = (queryParams: string) =>
  Object.fromEntries(new URLSearchParams(queryParams))

export const stringify = (queryParams: Record<string, string>) =>
  new URLSearchParams(queryParams).toString()
