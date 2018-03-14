const encode = (val) => {
  try {
    return encodeURIComponent(val);
  } catch (e) {
    console.error('error encode %o');
  }
  return null;
};

const decode = (val) => {
  try {
    return decodeURIComponent(val);
  } catch (err) {
    console.error('error decode %o');
  }
  return null;
};

const handleSkey = (sKey) => encode(sKey).replace(/[\-\.\+\*]/g, '\\$&');

const Cookies = {
  getItem(sKey) {
    if (!sKey) { return null; }
    return (
      decode(
        document.cookie
        .replace(
          new RegExp(`(?:(?:^|.*;)\\s*${handleSkey(sKey)}\\s*\\=\\s*([^;]*).*$)|^.*$`)
        , '$1')
      ) || null
    );
  },

  setItem(sKey, sValue, vEnd, sPath, sDomain, bSecure) {
    if (!sKey || /^(?:expires|max\-age|path|domain|secure)$/i.test(sKey)) { return false; }
    let sExpires = '';
    if (vEnd) {
      switch (vEnd.constructor) {
        case Number:
          if (vEnd === Infinity) {
            sExpires = '; expires=Fri, 31 Dec 9999 23:59:59 GMT';
          } else {
            sExpires = `; max-age=${vEnd}`;
          }
          break;
        case String:
          sExpires = `; expires=${vEnd}`;
          break;
        case Date:
          sExpires = `; expires=${vEnd.toUTCString()}`;
          break;
        default:
          break;
      }
    }
    document.cookie = [
      encode(sKey), '=', encode(sValue),
      sExpires,
      (sDomain ? `; domain=${sDomain}` : ''),
      (sPath ? `; path=${sPath}` : ''),
      (bSecure ? '; secure' : ''),
    ].join('');
    return true;
  },

  removeItem(sKey, sPath, sDomain) {
    if (!this.hasItem(sKey)) { return false; }
    document.cookie = [
      encode(sKey), '=; expires=Thu, 01 Jan 1970 00:00:00 GMT',
      (sDomain ? `; domain=${sDomain}` : ''),
      (sPath ? `; path=${sPath}` : ''),
    ].join('');
    return true;
  },

  hasItem(sKey) {
    if (!sKey) { return false; }
    return (
      new RegExp(`(?:^|;\\s*)${encode(sKey).replace(/[\-\.\+\*]/g, '\\$&')}\\s*\\=`)
    ).test(document.cookie);
  },

  keys() {
    let aKeys = document.cookie
    .replace(/((?:^|\s*;)[^\=]+)(?=;|$)|^\s*|\s*(?:\=[^;]*)?(?:\1|$)/g, '')
    .split(/\s*(?:\=[^;]*)?;\s*/);
    aKeys = aKeys.map((key) => decode(key));
    return aKeys;
  },
};

export default Cookies;
