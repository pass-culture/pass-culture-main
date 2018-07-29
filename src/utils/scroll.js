export function stopBodyScrolling(bool) {
  /*
  bool === true
    ? document.body.addEventListener("touchmove", freezeVp, false)
    : document.body.removeEventListener("touchmove", freezeVp, false)
  */
  bool === true
    ? document.body.classList.add('no-scroll')
    : document.body.classList.remove('no-scroll')
  console.log('document.body.classList', [...document.body.classList])
}
