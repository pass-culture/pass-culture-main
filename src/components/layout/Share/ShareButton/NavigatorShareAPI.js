export const share = nativeOptions => {
  return navigator.share(nativeOptions)
}

export default {
  share,
}
