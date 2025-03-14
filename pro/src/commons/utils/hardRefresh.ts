/**
 * Performs a complete page refresh by redirecting to the specified URL.
 * Having this as a helper makes it easier to mock in unit tests
 *
 * @param {string} to - The destination URL to redirect to
 * @returns {void}
 */
export const hardRefresh = (to: string): void => {
  window.location.href = to
}
