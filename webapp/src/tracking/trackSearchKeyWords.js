export default (keyWords, categories) => {
  const trackedCategories = categories || false
  const trackedKeyWords = keyWords || false
  const numberOfResults = false
  window._paq.push(['trackSiteSearch', trackedKeyWords, trackedCategories, numberOfResults])
}
