export function getConfigWithDefaultValues(config) {
  return {
    method: 'GET',
    ...config,
  }
}
