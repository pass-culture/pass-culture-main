export default text => {
  text = text.trim();
  return text.charAt(0).toUpperCase() + text.slice(1);
}