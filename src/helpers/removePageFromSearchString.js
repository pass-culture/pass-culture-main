const removePageFromSearchString = searchString =>
  searchString
    .split('&')
    .filter(element => !element.includes('page='))
    .join('&')

export default removePageFromSearchString
