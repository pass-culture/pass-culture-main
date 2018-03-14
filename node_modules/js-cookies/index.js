'use strict';

Object.defineProperty(exports, "__esModule", {
  value: true
});
var encode = function encode(val) {
  try {
    return encodeURIComponent(val);
  } catch (e) {
    console.error('error encode %o');
  }
  return null;
};

var decode = function decode(val) {
  try {
    return decodeURIComponent(val);
  } catch (err) {
    console.error('error decode %o');
  }
  return null;
};

var handleSkey = function handleSkey(sKey) {
  return encode(sKey).replace(/[\-\.\+\*]/g, '\\$&');
};

var Cookies = {
  getItem: function getItem(sKey) {
    if (!sKey) {
      return null;
    }
    return decode(document.cookie.replace(new RegExp('(?:(?:^|.*;)\\s*' + handleSkey(sKey) + '\\s*\\=\\s*([^;]*).*$)|^.*$'), '$1')) || null;
  },
  setItem: function setItem(sKey, sValue, vEnd, sPath, sDomain, bSecure) {
    if (!sKey || /^(?:expires|max\-age|path|domain|secure)$/i.test(sKey)) {
      return false;
    }
    var sExpires = '';
    if (vEnd) {
      switch (vEnd.constructor) {
        case Number:
          if (vEnd === Infinity) {
            sExpires = '; expires=Fri, 31 Dec 9999 23:59:59 GMT';
          } else {
            sExpires = '; max-age=' + vEnd;
          }
          break;
        case String:
          sExpires = '; expires=' + vEnd;
          break;
        case Date:
          sExpires = '; expires=' + vEnd.toUTCString();
          break;
        default:
          break;
      }
    }
    document.cookie = [encode(sKey), '=', encode(sValue), sExpires, sDomain ? '; domain=' + sDomain : '', sPath ? '; path=' + sPath : '', bSecure ? '; secure' : ''].join('');
    return true;
  },
  removeItem: function removeItem(sKey, sPath, sDomain) {
    if (!this.hasItem(sKey)) {
      return false;
    }
    document.cookie = [encode(sKey), '=; expires=Thu, 01 Jan 1970 00:00:00 GMT', sDomain ? '; domain=' + sDomain : '', sPath ? '; path=' + sPath : ''].join('');
    return true;
  },
  hasItem: function hasItem(sKey) {
    if (!sKey) {
      return false;
    }
    return new RegExp('(?:^|;\\s*)' + encode(sKey).replace(/[\-\.\+\*]/g, '\\$&') + '\\s*\\=').test(document.cookie);
  },
  keys: function keys() {
    var aKeys = document.cookie.replace(/((?:^|\s*;)[^\=]+)(?=;|$)|^\s*|\s*(?:\=[^;]*)?(?:\1|$)/g, '').split(/\s*(?:\=[^;]*)?;\s*/);
    aKeys = aKeys.map(function (key) {
      return decode(key);
    });
    return aKeys;
  }
};

exports.default = Cookies;
