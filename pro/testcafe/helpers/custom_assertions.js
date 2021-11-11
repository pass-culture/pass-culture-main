import { ClientFunction } from 'testcafe'

export const isElementInViewport = ClientFunction(selector => {
  const windowHeight = window.innerHeight
  const windowWidth = window.innerWidth

  const getBoundValues = document.querySelector(selector).getBoundingClientRect()
  return (
    getBoundValues.bottom > 0 &&
    getBoundValues.right > 0 &&
    getBoundValues.left < (windowWidth || document.documentElement.clientWidth) &&
    getBoundValues.top < (windowHeight || document.documentElement.clientHeight)
  )
})
