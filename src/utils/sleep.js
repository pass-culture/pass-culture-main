function sleep(milliseconds) {
  let start = new Date().getTime()
  for (let i = 0; i < 1e7; i++) {
    if (new Date().getTime() - start > milliseconds) {
      break
    }
  }
}
