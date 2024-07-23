import{j as k}from"./jsx-runtime-Nms4Y4qS.js";import{K as Ct}from"./index-BtHzObcb.js";import{r as It}from"./index-BwDkhjyp.js";import"./config-yp2pWrHW.js";import{u as Et}from"./index-DoFAhGZq.js";import{f as bt}from"./full-help-Co3hxUDJ.js";import{S as wt}from"./SvgIcon-Cibea2Sc.js";import"./_commonjsHelpers-BosuxZz1.js";import"./index-CReuRBEY.js";/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Pe=function(e){const t=[];let n=0;for(let r=0;r<e.length;r++){let a=e.charCodeAt(r);a<128?t[n++]=a:a<2048?(t[n++]=a>>6|192,t[n++]=a&63|128):(a&64512)===55296&&r+1<e.length&&(e.charCodeAt(r+1)&64512)===56320?(a=65536+((a&1023)<<10)+(e.charCodeAt(++r)&1023),t[n++]=a>>18|240,t[n++]=a>>12&63|128,t[n++]=a>>6&63|128,t[n++]=a&63|128):(t[n++]=a>>12|224,t[n++]=a>>6&63|128,t[n++]=a&63|128)}return t},St=function(e){const t=[];let n=0,r=0;for(;n<e.length;){const a=e[n++];if(a<128)t[r++]=String.fromCharCode(a);else if(a>191&&a<224){const s=e[n++];t[r++]=String.fromCharCode((a&31)<<6|s&63)}else if(a>239&&a<365){const s=e[n++],i=e[n++],c=e[n++],o=((a&7)<<18|(s&63)<<12|(i&63)<<6|c&63)-65536;t[r++]=String.fromCharCode(55296+(o>>10)),t[r++]=String.fromCharCode(56320+(o&1023))}else{const s=e[n++],i=e[n++];t[r++]=String.fromCharCode((a&15)<<12|(s&63)<<6|i&63)}}return t.join("")},Tt={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(e,t){if(!Array.isArray(e))throw Error("encodeByteArray takes an array as a parameter");this.init_();const n=t?this.byteToCharMapWebSafe_:this.byteToCharMap_,r=[];for(let a=0;a<e.length;a+=3){const s=e[a],i=a+1<e.length,c=i?e[a+1]:0,o=a+2<e.length,l=o?e[a+2]:0,d=s>>2,h=(s&3)<<4|c>>4;let f=(c&15)<<2|l>>6,g=l&63;o||(g=64,i||(f=64)),r.push(n[d],n[h],n[f],n[g])}return r.join("")},encodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?btoa(e):this.encodeByteArray(Pe(e),t)},decodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?atob(e):St(this.decodeStringToByteArray(e,t))},decodeStringToByteArray(e,t){this.init_();const n=t?this.charToByteMapWebSafe_:this.charToByteMap_,r=[];for(let a=0;a<e.length;){const s=n[e.charAt(a++)],c=a<e.length?n[e.charAt(a)]:0;++a;const l=a<e.length?n[e.charAt(a)]:64;++a;const h=a<e.length?n[e.charAt(a)]:64;if(++a,s==null||c==null||l==null||h==null)throw new yt;const f=s<<2|c>>4;if(r.push(f),l!==64){const g=c<<4&240|l>>2;if(r.push(g),h!==64){const E=l<<6&192|h;r.push(E)}}}return r},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let e=0;e<this.ENCODED_VALS.length;e++)this.byteToCharMap_[e]=this.ENCODED_VALS.charAt(e),this.charToByteMap_[this.byteToCharMap_[e]]=e,this.byteToCharMapWebSafe_[e]=this.ENCODED_VALS_WEBSAFE.charAt(e),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[e]]=e,e>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(e)]=e,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(e)]=e)}}};class yt extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const At=function(e){const t=Pe(e);return Tt.encodeByteArray(t,!0)},Be=function(e){return At(e).replace(/\./g,"")};function Dt(){const e=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof e=="object"&&e.id!==void 0}function re(){try{return typeof indexedDB=="object"}catch{return!1}}function $e(){return new Promise((e,t)=>{try{let n=!0;const r="validate-browser-context-for-indexeddb-analytics-module",a=self.indexedDB.open(r);a.onsuccess=()=>{a.result.close(),n||self.indexedDB.deleteDatabase(r),e(!0)},a.onupgradeneeded=()=>{n=!1},a.onerror=()=>{var s;t(((s=a.error)===null||s===void 0?void 0:s.message)||"")}}catch(n){t(n)}})}function Ot(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Lt="FirebaseError";class y extends Error{constructor(t,n,r){super(n),this.code=t,this.customData=r,this.name=Lt,Object.setPrototypeOf(this,y.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,M.prototype.create)}}class M{constructor(t,n,r){this.service=t,this.serviceName=n,this.errors=r}create(t,...n){const r=n[0]||{},a=`${this.service}/${t}`,s=this.errors[t],i=s?Rt(s,r):"Error",c=`${this.serviceName}: ${i} (${a}).`;return new y(a,c,r)}}function Rt(e,t){return e.replace(Ft,(n,r)=>{const a=t[r];return a!=null?String(a):`<${r}?>`})}const Ft=/\{\$([^}]+)}/g;/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const kt=1e3,Nt=2,vt=4*60*60*1e3,Mt=.5;function Q(e,t=kt,n=Nt){const r=t*Math.pow(n,e),a=Math.round(Mt*r*(Math.random()-.5)*2);return Math.min(vt,r+a)}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Ke(e){return e&&e._delegate?e._delegate:e}class S{constructor(t,n,r){this.name=t,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */var u;(function(e){e[e.DEBUG=0]="DEBUG",e[e.VERBOSE=1]="VERBOSE",e[e.INFO=2]="INFO",e[e.WARN=3]="WARN",e[e.ERROR=4]="ERROR",e[e.SILENT=5]="SILENT"})(u||(u={}));const Pt={debug:u.DEBUG,verbose:u.VERBOSE,info:u.INFO,warn:u.WARN,error:u.ERROR,silent:u.SILENT},Bt=u.INFO,$t={[u.DEBUG]:"log",[u.VERBOSE]:"log",[u.INFO]:"info",[u.WARN]:"warn",[u.ERROR]:"error"},Kt=(e,t,...n)=>{if(t<e.logLevel)return;const r=new Date().toISOString(),a=$t[t];if(a)console[a](`[${r}]  ${e.name}:`,...n);else throw new Error(`Attempted to log a message with an invalid logType (value: ${t})`)};class ae{constructor(t){this.name=t,this._logLevel=Bt,this._logHandler=Kt,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(t){if(!(t in u))throw new TypeError(`Invalid value "${t}" assigned to \`logLevel\``);this._logLevel=t}setLogLevel(t){this._logLevel=typeof t=="string"?Pt[t]:t}get logHandler(){return this._logHandler}set logHandler(t){if(typeof t!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=t}get userLogHandler(){return this._userLogHandler}set userLogHandler(t){this._userLogHandler=t}debug(...t){this._userLogHandler&&this._userLogHandler(this,u.DEBUG,...t),this._logHandler(this,u.DEBUG,...t)}log(...t){this._userLogHandler&&this._userLogHandler(this,u.VERBOSE,...t),this._logHandler(this,u.VERBOSE,...t)}info(...t){this._userLogHandler&&this._userLogHandler(this,u.INFO,...t),this._logHandler(this,u.INFO,...t)}warn(...t){this._userLogHandler&&this._userLogHandler(this,u.WARN,...t),this._logHandler(this,u.WARN,...t)}error(...t){this._userLogHandler&&this._userLogHandler(this,u.ERROR,...t),this._logHandler(this,u.ERROR,...t)}}const Ht=(e,t)=>t.some(n=>e instanceof n);let he,fe;function Ut(){return he||(he=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function xt(){return fe||(fe=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const He=new WeakMap,Z=new WeakMap,Ue=new WeakMap,j=new WeakMap,se=new WeakMap;function Vt(e){const t=new Promise((n,r)=>{const a=()=>{e.removeEventListener("success",s),e.removeEventListener("error",i)},s=()=>{n(w(e.result)),a()},i=()=>{r(e.error),a()};e.addEventListener("success",s),e.addEventListener("error",i)});return t.then(n=>{n instanceof IDBCursor&&He.set(n,e)}).catch(()=>{}),se.set(t,e),t}function jt(e){if(Z.has(e))return;const t=new Promise((n,r)=>{const a=()=>{e.removeEventListener("complete",s),e.removeEventListener("error",i),e.removeEventListener("abort",i)},s=()=>{n(),a()},i=()=>{r(e.error||new DOMException("AbortError","AbortError")),a()};e.addEventListener("complete",s),e.addEventListener("error",i),e.addEventListener("abort",i)});Z.set(e,t)}let ee={get(e,t,n){if(e instanceof IDBTransaction){if(t==="done")return Z.get(e);if(t==="objectStoreNames")return e.objectStoreNames||Ue.get(e);if(t==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return w(e[t])},set(e,t,n){return e[t]=n,!0},has(e,t){return e instanceof IDBTransaction&&(t==="done"||t==="store")?!0:t in e}};function Gt(e){ee=e(ee)}function Wt(e){return e===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(t,...n){const r=e.call(G(this),t,...n);return Ue.set(r,t.sort?t.sort():[t]),w(r)}:xt().includes(e)?function(...t){return e.apply(G(this),t),w(He.get(this))}:function(...t){return w(e.apply(G(this),t))}}function qt(e){return typeof e=="function"?Wt(e):(e instanceof IDBTransaction&&jt(e),Ht(e,Ut())?new Proxy(e,ee):e)}function w(e){if(e instanceof IDBRequest)return Vt(e);if(j.has(e))return j.get(e);const t=qt(e);return t!==e&&(j.set(e,t),se.set(t,e)),t}const G=e=>se.get(e);function xe(e,t,{blocked:n,upgrade:r,blocking:a,terminated:s}={}){const i=indexedDB.open(e,t),c=w(i);return r&&i.addEventListener("upgradeneeded",o=>{r(w(i.result),o.oldVersion,o.newVersion,w(i.transaction),o)}),n&&i.addEventListener("blocked",o=>n(o.oldVersion,o.newVersion,o)),c.then(o=>{s&&o.addEventListener("close",()=>s()),a&&o.addEventListener("versionchange",l=>a(l.oldVersion,l.newVersion,l))}).catch(()=>{}),c}const zt=["get","getKey","getAll","getAllKeys","count"],Yt=["put","add","delete","clear"],W=new Map;function ge(e,t){if(!(e instanceof IDBDatabase&&!(t in e)&&typeof t=="string"))return;if(W.get(t))return W.get(t);const n=t.replace(/FromIndex$/,""),r=t!==n,a=Yt.includes(n);if(!(n in(r?IDBIndex:IDBObjectStore).prototype)||!(a||zt.includes(n)))return;const s=async function(i,...c){const o=this.transaction(i,a?"readwrite":"readonly");let l=o.store;return r&&(l=l.index(c.shift())),(await Promise.all([l[n](...c),a&&o.done]))[0]};return W.set(t,s),s}Gt(e=>({...e,get:(t,n,r)=>ge(t,n)||e.get(t,n,r),has:(t,n)=>!!ge(t,n)||e.has(t,n)}));/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Jt{constructor(t){this.container=t}getPlatformInfoString(){return this.container.getProviders().map(n=>{if(Xt(n)){const r=n.getImmediate();return`${r.library}/${r.version}`}else return null}).filter(n=>n).join(" ")}}function Xt(e){const t=e.getComponent();return(t==null?void 0:t.type)==="VERSION"}const te="@firebase/app",pe="0.10.7";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const O=new ae("@firebase/app"),Qt="@firebase/app-compat",Zt="@firebase/analytics-compat",en="@firebase/analytics",tn="@firebase/app-check-compat",nn="@firebase/app-check",rn="@firebase/auth",an="@firebase/auth-compat",sn="@firebase/database",on="@firebase/database-compat",cn="@firebase/functions",ln="@firebase/functions-compat",un="@firebase/installations",dn="@firebase/installations-compat",hn="@firebase/messaging",fn="@firebase/messaging-compat",gn="@firebase/performance",pn="@firebase/performance-compat",mn="@firebase/remote-config",_n="@firebase/remote-config-compat",Cn="@firebase/storage",In="@firebase/storage-compat",En="@firebase/firestore",bn="@firebase/vertexai-preview",wn="@firebase/firestore-compat",Sn="firebase",Tn="10.12.4",yn={[te]:"fire-core",[Qt]:"fire-core-compat",[en]:"fire-analytics",[Zt]:"fire-analytics-compat",[nn]:"fire-app-check",[tn]:"fire-app-check-compat",[rn]:"fire-auth",[an]:"fire-auth-compat",[sn]:"fire-rtdb",[on]:"fire-rtdb-compat",[cn]:"fire-fn",[ln]:"fire-fn-compat",[un]:"fire-iid",[dn]:"fire-iid-compat",[hn]:"fire-fcm",[fn]:"fire-fcm-compat",[gn]:"fire-perf",[pn]:"fire-perf-compat",[mn]:"fire-rc",[_n]:"fire-rc-compat",[Cn]:"fire-gcs",[In]:"fire-gcs-compat",[En]:"fire-fst",[wn]:"fire-fst-compat",[bn]:"fire-vertex","fire-js":"fire-js",[Sn]:"fire-js-all"};/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const An=new Map,Dn=new Map,me=new Map;function _e(e,t){try{e.container.addComponent(t)}catch(n){O.debug(`Component ${t.name} failed to register with FirebaseApp ${e.name}`,n)}}function T(e){const t=e.name;if(me.has(t))return O.debug(`There were multiple attempts to register component ${t}.`),!1;me.set(t,e);for(const n of An.values())_e(n,e);for(const n of Dn.values())_e(n,e);return!0}function Ve(e,t){const n=e.container.getProvider("heartbeat").getImmediate({optional:!0});return n&&n.triggerHeartbeat(),e.container.getProvider(t)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const On={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},ie=new M("app","Firebase",On);/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ln=Tn;function I(e,t,n){var r;let a=(r=yn[e])!==null&&r!==void 0?r:e;n&&(a+=`-${n}`);const s=a.match(/\s|\//),i=t.match(/\s|\//);if(s||i){const c=[`Unable to register library "${a}" with version "${t}":`];s&&c.push(`library name "${a}" contains illegal characters (whitespace or "/")`),s&&i&&c.push("and"),i&&c.push(`version name "${t}" contains illegal characters (whitespace or "/")`),O.warn(c.join(" "));return}T(new S(`${a}-version`,()=>({library:a,version:t}),"VERSION"))}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Rn="firebase-heartbeat-database",Fn=1,v="firebase-heartbeat-store";let q=null;function je(){return q||(q=xe(Rn,Fn,{upgrade:(e,t)=>{switch(t){case 0:try{e.createObjectStore(v)}catch(n){console.warn(n)}}}}).catch(e=>{throw ie.create("idb-open",{originalErrorMessage:e.message})})),q}async function kn(e){try{const n=(await je()).transaction(v),r=await n.objectStore(v).get(Ge(e));return await n.done,r}catch(t){if(t instanceof y)O.warn(t.message);else{const n=ie.create("idb-get",{originalErrorMessage:t==null?void 0:t.message});O.warn(n.message)}}}async function Ce(e,t){try{const r=(await je()).transaction(v,"readwrite");await r.objectStore(v).put(t,Ge(e)),await r.done}catch(n){if(n instanceof y)O.warn(n.message);else{const r=ie.create("idb-set",{originalErrorMessage:n==null?void 0:n.message});O.warn(r.message)}}}function Ge(e){return`${e.name}!${e.options.appId}`}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Nn=1024,vn=30*24*60*60*1e3;class Mn{constructor(t){this.container=t,this._heartbeatsCache=null;const n=this.container.getProvider("app").getImmediate();this._storage=new Bn(n),this._heartbeatsCachePromise=this._storage.read().then(r=>(this._heartbeatsCache=r,r))}async triggerHeartbeat(){var t,n;const a=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),s=Ie();if(!(((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,((n=this._heartbeatsCache)===null||n===void 0?void 0:n.heartbeats)==null))&&!(this._heartbeatsCache.lastSentHeartbeatDate===s||this._heartbeatsCache.heartbeats.some(i=>i.date===s)))return this._heartbeatsCache.heartbeats.push({date:s,agent:a}),this._heartbeatsCache.heartbeats=this._heartbeatsCache.heartbeats.filter(i=>{const c=new Date(i.date).valueOf();return Date.now()-c<=vn}),this._storage.overwrite(this._heartbeatsCache)}async getHeartbeatsHeader(){var t;if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null||this._heartbeatsCache.heartbeats.length===0)return"";const n=Ie(),{heartbeatsToSend:r,unsentEntries:a}=Pn(this._heartbeatsCache.heartbeats),s=Be(JSON.stringify({version:2,heartbeats:r}));return this._heartbeatsCache.lastSentHeartbeatDate=n,a.length>0?(this._heartbeatsCache.heartbeats=a,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),s}}function Ie(){return new Date().toISOString().substring(0,10)}function Pn(e,t=Nn){const n=[];let r=e.slice();for(const a of e){const s=n.find(i=>i.agent===a.agent);if(s){if(s.dates.push(a.date),Ee(n)>t){s.dates.pop();break}}else if(n.push({agent:a.agent,dates:[a.date]}),Ee(n)>t){n.pop();break}r=r.slice(1)}return{heartbeatsToSend:n,unsentEntries:r}}class Bn{constructor(t){this.app=t,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return re()?$e().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const n=await kn(this.app);return n!=null&&n.heartbeats?n:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(t){var n;if(await this._canUseIndexedDBPromise){const a=await this.read();return Ce(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:a.lastSentHeartbeatDate,heartbeats:t.heartbeats})}else return}async add(t){var n;if(await this._canUseIndexedDBPromise){const a=await this.read();return Ce(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:a.lastSentHeartbeatDate,heartbeats:[...a.heartbeats,...t.heartbeats]})}else return}}function Ee(e){return Be(JSON.stringify({version:2,heartbeats:e})).length}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function $n(e){T(new S("platform-logger",t=>new Jt(t),"PRIVATE")),T(new S("heartbeat",t=>new Mn(t),"PRIVATE")),I(te,pe,e),I(te,pe,"esm2017"),I("fire-js","")}$n("");/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */const Kn={};/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */function P(e){return Object.isFrozen(e)&&Object.isFrozen(e.raw)}function B(e){return e.toString().indexOf("`")===-1}B(e=>e``)||B(e=>e`\0`)||B(e=>e`\n`)||B(e=>e`\u0000`);P``&&P`\0`&&P`\n`&&P`\u0000`;/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */let We="google#safe";function Hn(){if(typeof window<"u")return window.trustedTypes}function qe(){var e;return We!==""&&(e=Hn())!==null&&e!==void 0?e:null}let $;function Un(){var e,t;if($===void 0)try{$=(t=(e=qe())===null||e===void 0?void 0:e.createPolicy(We,{createHTML:n=>n,createScript:n=>n,createScriptURL:n=>n}))!==null&&t!==void 0?t:null}catch{$=null}return $}/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */class ze{constructor(t,n){this.privateDoNotAccessOrElseWrappedResourceUrl=t}toString(){return this.privateDoNotAccessOrElseWrappedResourceUrl.toString()}}function be(e){var t;const n=e,r=(t=Un())===null||t===void 0?void 0:t.createScriptURL(n);return r??new ze(n,Kn)}function xn(e){var t;if(!((t=qe())===null||t===void 0)&&t.isScriptURL(e))return e;if(e instanceof ze)return e.privateDoNotAccessOrElseWrappedResourceUrl;{let n="";throw new Error(n)}}/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */function Vn(e,...t){if(t.length===0)return be(e[0]);e[0].toLowerCase();let n=e[0];for(let r=0;r<t.length;r++)n+=encodeURIComponent(t[r])+e[r+1];return be(n)}/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */function jn(e){return Gn("script",e)}function Gn(e,t){var n;const r=t.document,a=(n=r.querySelector)===null||n===void 0?void 0:n.call(r,`${e}[nonce]`);return a&&(a.nonce||a.getAttribute("nonce"))||""}/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */function Wn(e){const t=e.ownerDocument&&e.ownerDocument.defaultView,n=jn(t||window);n&&e.setAttribute("nonce",n)}function qn(e,t,n){e.src=xn(t),!(n!=null&&n.omitNonce)&&Wn(e)}const Ye="@firebase/installations",oe="0.6.8";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Je=1e4,Xe=`w:${oe}`,Qe="FIS_v2",zn="https://firebaseinstallations.googleapis.com/v1",Yn=60*60*1e3,Jn="installations",Xn="Installations";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Qn={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},L=new M(Jn,Xn,Qn);function Ze(e){return e instanceof y&&e.code.includes("request-failed")}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function et({projectId:e}){return`${zn}/projects/${e}/installations`}function tt(e){return{token:e.token,requestStatus:2,expiresIn:er(e.expiresIn),creationTime:Date.now()}}async function nt(e,t){const r=(await t.json()).error;return L.create("request-failed",{requestName:e,serverCode:r.code,serverMessage:r.message,serverStatus:r.status})}function rt({apiKey:e}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e})}function Zn(e,{refreshToken:t}){const n=rt(e);return n.append("Authorization",tr(t)),n}async function at(e){const t=await e();return t.status>=500&&t.status<600?e():t}function er(e){return Number(e.replace("s","000"))}function tr(e){return`${Qe} ${e}`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function nr({appConfig:e,heartbeatServiceProvider:t},{fid:n}){const r=et(e),a=rt(e),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&a.append("x-firebase-client",l)}const i={fid:n,authVersion:Qe,appId:e.appId,sdkVersion:Xe},c={method:"POST",headers:a,body:JSON.stringify(i)},o=await at(()=>fetch(r,c));if(o.ok){const l=await o.json();return{fid:l.fid||n,registrationStatus:2,refreshToken:l.refreshToken,authToken:tt(l.authToken)}}else throw await nt("Create Installation",o)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function st(e){return new Promise(t=>{setTimeout(t,e)})}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function rr(e){return btoa(String.fromCharCode(...e)).replace(/\+/g,"-").replace(/\//g,"_")}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ar=/^[cdef][\w-]{21}$/,ne="";function sr(){try{const e=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(e),e[0]=112+e[0]%16;const n=ir(e);return ar.test(n)?n:ne}catch{return ne}}function ir(e){return rr(e).substr(0,22)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function x(e){return`${e.appName}!${e.appId}`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const it=new Map;function ot(e,t){const n=x(e);ct(n,t),or(n,t)}function ct(e,t){const n=it.get(e);if(n)for(const r of n)r(t)}function or(e,t){const n=cr();n&&n.postMessage({key:e,fid:t}),lr()}let D=null;function cr(){return!D&&"BroadcastChannel"in self&&(D=new BroadcastChannel("[Firebase] FID Change"),D.onmessage=e=>{ct(e.data.key,e.data.fid)}),D}function lr(){it.size===0&&D&&(D.close(),D=null)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ur="firebase-installations-database",dr=1,R="firebase-installations-store";let z=null;function ce(){return z||(z=xe(ur,dr,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(R)}}})),z}async function U(e,t){const n=x(e),a=(await ce()).transaction(R,"readwrite"),s=a.objectStore(R),i=await s.get(n);return await s.put(t,n),await a.done,(!i||i.fid!==t.fid)&&ot(e,t.fid),t}async function lt(e){const t=x(e),r=(await ce()).transaction(R,"readwrite");await r.objectStore(R).delete(t),await r.done}async function V(e,t){const n=x(e),a=(await ce()).transaction(R,"readwrite"),s=a.objectStore(R),i=await s.get(n),c=t(i);return c===void 0?await s.delete(n):await s.put(c,n),await a.done,c&&(!i||i.fid!==c.fid)&&ot(e,c.fid),c}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function le(e){let t;const n=await V(e.appConfig,r=>{const a=hr(r),s=fr(e,a);return t=s.registrationPromise,s.installationEntry});return n.fid===ne?{installationEntry:await t}:{installationEntry:n,registrationPromise:t}}function hr(e){const t=e||{fid:sr(),registrationStatus:0};return ut(t)}function fr(e,t){if(t.registrationStatus===0){if(!navigator.onLine){const a=Promise.reject(L.create("app-offline"));return{installationEntry:t,registrationPromise:a}}const n={fid:t.fid,registrationStatus:1,registrationTime:Date.now()},r=gr(e,n);return{installationEntry:n,registrationPromise:r}}else return t.registrationStatus===1?{installationEntry:t,registrationPromise:pr(e)}:{installationEntry:t}}async function gr(e,t){try{const n=await nr(e,t);return U(e.appConfig,n)}catch(n){throw Ze(n)&&n.customData.serverCode===409?await lt(e.appConfig):await U(e.appConfig,{fid:t.fid,registrationStatus:0}),n}}async function pr(e){let t=await we(e.appConfig);for(;t.registrationStatus===1;)await st(100),t=await we(e.appConfig);if(t.registrationStatus===0){const{installationEntry:n,registrationPromise:r}=await le(e);return r||n}return t}function we(e){return V(e,t=>{if(!t)throw L.create("installation-not-found");return ut(t)})}function ut(e){return mr(e)?{fid:e.fid,registrationStatus:0}:e}function mr(e){return e.registrationStatus===1&&e.registrationTime+Je<Date.now()}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function _r({appConfig:e,heartbeatServiceProvider:t},n){const r=Cr(e,n),a=Zn(e,n),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&a.append("x-firebase-client",l)}const i={installation:{sdkVersion:Xe,appId:e.appId}},c={method:"POST",headers:a,body:JSON.stringify(i)},o=await at(()=>fetch(r,c));if(o.ok){const l=await o.json();return tt(l)}else throw await nt("Generate Auth Token",o)}function Cr(e,{fid:t}){return`${et(e)}/${t}/authTokens:generate`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function ue(e,t=!1){let n;const r=await V(e.appConfig,s=>{if(!dt(s))throw L.create("not-registered");const i=s.authToken;if(!t&&br(i))return s;if(i.requestStatus===1)return n=Ir(e,t),s;{if(!navigator.onLine)throw L.create("app-offline");const c=Sr(s);return n=Er(e,c),c}});return n?await n:r.authToken}async function Ir(e,t){let n=await Se(e.appConfig);for(;n.authToken.requestStatus===1;)await st(100),n=await Se(e.appConfig);const r=n.authToken;return r.requestStatus===0?ue(e,t):r}function Se(e){return V(e,t=>{if(!dt(t))throw L.create("not-registered");const n=t.authToken;return Tr(n)?Object.assign(Object.assign({},t),{authToken:{requestStatus:0}}):t})}async function Er(e,t){try{const n=await _r(e,t),r=Object.assign(Object.assign({},t),{authToken:n});return await U(e.appConfig,r),n}catch(n){if(Ze(n)&&(n.customData.serverCode===401||n.customData.serverCode===404))await lt(e.appConfig);else{const r=Object.assign(Object.assign({},t),{authToken:{requestStatus:0}});await U(e.appConfig,r)}throw n}}function dt(e){return e!==void 0&&e.registrationStatus===2}function br(e){return e.requestStatus===2&&!wr(e)}function wr(e){const t=Date.now();return t<e.creationTime||e.creationTime+e.expiresIn<t+Yn}function Sr(e){const t={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},e),{authToken:t})}function Tr(e){return e.requestStatus===1&&e.requestTime+Je<Date.now()}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function yr(e){const t=e,{installationEntry:n,registrationPromise:r}=await le(t);return r?r.catch(console.error):ue(t).catch(console.error),n.fid}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Ar(e,t=!1){const n=e;return await Dr(n),(await ue(n,t)).token}async function Dr(e){const{registrationPromise:t}=await le(e);t&&await t}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Or(e){if(!e||!e.options)throw Y("App Configuration");if(!e.name)throw Y("App Name");const t=["projectId","apiKey","appId"];for(const n of t)if(!e.options[n])throw Y(n);return{appName:e.name,projectId:e.options.projectId,apiKey:e.options.apiKey,appId:e.options.appId}}function Y(e){return L.create("missing-app-config-values",{valueName:e})}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ht="installations",Lr="installations-internal",Rr=e=>{const t=e.getProvider("app").getImmediate(),n=Or(t),r=Ve(t,"heartbeat");return{app:t,appConfig:n,heartbeatServiceProvider:r,_delete:()=>Promise.resolve()}},Fr=e=>{const t=e.getProvider("app").getImmediate(),n=Ve(t,ht).getImmediate();return{getId:()=>yr(n),getToken:a=>Ar(n,a)}};function kr(){T(new S(ht,Rr,"PUBLIC")),T(new S(Lr,Fr,"PRIVATE"))}kr();I(Ye,oe);I(Ye,oe,"esm2017");/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Te="analytics",Nr="firebase_id",vr="origin",Mr=60*1e3,Pr="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",Br="https://www.googletagmanager.com/gtag/js";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const m=new ae("@firebase/analytics");/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function ft(e){return Promise.all(e.map(t=>t.catch(n=>n)))}function $r(e,t){const n=document.createElement("script"),r=Vn`https://www.googletagmanager.com/gtag/js?l=${e}&id=${t}`;qn(n,r),n.async=!0,document.head.appendChild(n)}function Kr(e){let t=[];return Array.isArray(window[e])?t=window[e]:window[e]=t,t}async function Hr(e,t,n,r,a,s){const i=r[a];try{if(i)await t[i];else{const o=(await ft(n)).find(l=>l.measurementId===a);o&&await t[o.appId]}}catch(c){m.error(c)}e("config",a,s)}async function Ur(e,t,n,r,a){try{let s=[];if(a&&a.send_to){let i=a.send_to;Array.isArray(i)||(i=[i]);const c=await ft(n);for(const o of i){const l=c.find(h=>h.measurementId===o),d=l&&t[l.appId];if(d)s.push(d);else{s=[];break}}}s.length===0&&(s=Object.values(t)),await Promise.all(s),e("event",r,a||{})}catch(s){m.error(s)}}function xr(e,t,n,r){async function a(s,...i){try{if(s==="event"){const[c,o]=i;await Ur(e,t,n,c,o)}else if(s==="config"){const[c,o]=i;await Hr(e,t,n,r,c,o)}else if(s==="consent"){const[c,o]=i;e("consent",c,o)}else if(s==="get"){const[c,o,l]=i;e("get",c,o,l)}else if(s==="set"){const[c]=i;e("set",c)}else e(s,...i)}catch(c){m.error(c)}}return a}function Vr(e,t,n,r,a){let s=function(...i){window[r].push(arguments)};return window[a]&&typeof window[a]=="function"&&(s=window[a]),window[a]=xr(s,e,t,n),{gtagCore:s,wrappedGtag:window[a]}}function jr(e){const t=window.document.getElementsByTagName("script");for(const n of Object.values(t))if(n.src&&n.src.includes(Br)&&n.src.includes(e))return n;return null}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Gr={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-intialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},C=new M("analytics","Analytics",Gr);/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Wr=30,qr=1e3;class zr{constructor(t={},n=qr){this.throttleMetadata=t,this.intervalMillis=n}getThrottleMetadata(t){return this.throttleMetadata[t]}setThrottleMetadata(t,n){this.throttleMetadata[t]=n}deleteThrottleMetadata(t){delete this.throttleMetadata[t]}}const gt=new zr;function Yr(e){return new Headers({Accept:"application/json","x-goog-api-key":e})}async function Jr(e){var t;const{appId:n,apiKey:r}=e,a={method:"GET",headers:Yr(r)},s=Pr.replace("{app-id}",n),i=await fetch(s,a);if(i.status!==200&&i.status!==304){let c="";try{const o=await i.json();!((t=o.error)===null||t===void 0)&&t.message&&(c=o.error.message)}catch{}throw C.create("config-fetch-failed",{httpStatus:i.status,responseMessage:c})}return i.json()}async function Xr(e,t=gt,n){const{appId:r,apiKey:a,measurementId:s}=e.options;if(!r)throw C.create("no-app-id");if(!a){if(s)return{measurementId:s,appId:r};throw C.create("no-api-key")}const i=t.getThrottleMetadata(r)||{backoffCount:0,throttleEndTimeMillis:Date.now()},c=new ea;return setTimeout(async()=>{c.abort()},n!==void 0?n:Mr),pt({appId:r,apiKey:a,measurementId:s},i,c,t)}async function pt(e,{throttleEndTimeMillis:t,backoffCount:n},r,a=gt){var s;const{appId:i,measurementId:c}=e;try{await Qr(r,t)}catch(o){if(c)return m.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${c} provided in the "measurementId" field in the local Firebase config. [${o==null?void 0:o.message}]`),{appId:i,measurementId:c};throw o}try{const o=await Jr(e);return a.deleteThrottleMetadata(i),o}catch(o){const l=o;if(!Zr(l)){if(a.deleteThrottleMetadata(i),c)return m.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${c} provided in the "measurementId" field in the local Firebase config. [${l==null?void 0:l.message}]`),{appId:i,measurementId:c};throw o}const d=Number((s=l==null?void 0:l.customData)===null||s===void 0?void 0:s.httpStatus)===503?Q(n,a.intervalMillis,Wr):Q(n,a.intervalMillis),h={throttleEndTimeMillis:Date.now()+d,backoffCount:n+1};return a.setThrottleMetadata(i,h),m.debug(`Calling attemptFetch again in ${d} millis`),pt(e,h,r,a)}}function Qr(e,t){return new Promise((n,r)=>{const a=Math.max(t-Date.now(),0),s=setTimeout(n,a);e.addEventListener(()=>{clearTimeout(s),r(C.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function Zr(e){if(!(e instanceof y)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class ea{constructor(){this.listeners=[]}addEventListener(t){this.listeners.push(t)}abort(){this.listeners.forEach(t=>t())}}async function ta(e,t,n,r,a){if(a&&a.global){e("event",n,r);return}else{const s=await t,i=Object.assign(Object.assign({},r),{send_to:s});e("event",n,i)}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function na(){if(re())try{await $e()}catch(e){return m.warn(C.create("indexeddb-unavailable",{errorInfo:e==null?void 0:e.toString()}).message),!1}else return m.warn(C.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function ra(e,t,n,r,a,s,i){var c;const o=Xr(e);o.then(g=>{n[g.measurementId]=g.appId,e.options.measurementId&&g.measurementId!==e.options.measurementId&&m.warn(`The measurement ID in the local Firebase config (${e.options.measurementId}) does not match the measurement ID fetched from the server (${g.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(g=>m.error(g)),t.push(o);const l=na().then(g=>{if(g)return r.getId()}),[d,h]=await Promise.all([o,l]);jr(s)||$r(s,d.measurementId),a("js",new Date);const f=(c=i==null?void 0:i.config)!==null&&c!==void 0?c:{};return f[vr]="firebase",f.update=!0,h!=null&&(f[Nr]=h),a("config",d.measurementId,f),d.measurementId}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class aa{constructor(t){this.app=t}_delete(){return delete N[this.app.options.appId],Promise.resolve()}}let N={},ye=[];const Ae={};let J="dataLayer",sa="gtag",De,mt,Oe=!1;function ia(){const e=[];if(Dt()&&e.push("This is a browser extension environment."),Ot()||e.push("Cookies are not available."),e.length>0){const t=e.map((r,a)=>`(${a+1}) ${r}`).join(" "),n=C.create("invalid-analytics-context",{errorInfo:t});m.warn(n.message)}}function oa(e,t,n){ia();const r=e.options.appId;if(!r)throw C.create("no-app-id");if(!e.options.apiKey)if(e.options.measurementId)m.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${e.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw C.create("no-api-key");if(N[r]!=null)throw C.create("already-exists",{id:r});if(!Oe){Kr(J);const{wrappedGtag:s,gtagCore:i}=Vr(N,ye,Ae,J,sa);mt=s,De=i,Oe=!0}return N[r]=ra(e,ye,Ae,t,De,J,n),new aa(e)}function ca(e,t,n,r){e=Ke(e),ta(mt,N[e.app.options.appId],t,n,r).catch(a=>m.error(a))}const Le="@firebase/analytics",Re="0.10.6";function la(){T(new S(Te,(t,{options:n})=>{const r=t.getProvider("app").getImmediate(),a=t.getProvider("installations-internal").getImmediate();return oa(r,a,n)},"PUBLIC")),T(new S("analytics-internal",e,"PRIVATE")),I(Le,Re),I(Le,Re,"esm2017");function e(t){try{const n=t.getProvider(Te).getImmediate();return{logEvent:(r,a,s)=>ca(n,r,a,s)}}catch(n){throw C.create("interop-component-reg-failed",{reason:n})}}}la();const X="@firebase/remote-config",Fe="0.4.8";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ua="remote-config";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const da={"registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser"},p=new M("remoteconfig","Remote Config",da);function ha(e){const t=Ke(e);return t._initializePromise||(t._initializePromise=t._storageCache.loadFromStorage().then(()=>{t._isInitializationComplete=!0})),t._initializePromise}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class fa{constructor(t,n,r,a){this.client=t,this.storage=n,this.storageCache=r,this.logger=a}isCachedDataFresh(t,n){if(!n)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const r=Date.now()-n,a=r<=t;return this.logger.debug(`Config fetch cache check. Cache age millis: ${r}. Cache max age millis (minimumFetchIntervalMillis setting): ${t}. Is cache hit: ${a}.`),a}async fetch(t){const[n,r]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(r&&this.isCachedDataFresh(t.cacheMaxAgeMillis,n))return r;t.eTag=r&&r.eTag;const a=await this.client.fetch(t),s=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return a.status===200&&s.push(this.storage.setLastSuccessfulFetchResponse(a)),await Promise.all(s),a}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function ga(e=navigator){return e.languages&&e.languages[0]||e.language}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class pa{constructor(t,n,r,a,s,i){this.firebaseInstallations=t,this.sdkVersion=n,this.namespace=r,this.projectId=a,this.apiKey=s,this.appId=i}async fetch(t){const[n,r]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),s=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,i={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":t.eTag||"*"},c={sdk_version:this.sdkVersion,app_instance_id:n,app_instance_id_token:r,app_id:this.appId,language_code:ga()},o={method:"POST",headers:i,body:JSON.stringify(c)},l=fetch(s,o),d=new Promise((_,b)=>{t.signal.addEventListener(()=>{const de=new Error("The operation was aborted.");de.name="AbortError",b(de)})});let h;try{await Promise.race([l,d]),h=await l}catch(_){let b="fetch-client-network";throw(_==null?void 0:_.name)==="AbortError"&&(b="fetch-timeout"),p.create(b,{originalErrorMessage:_==null?void 0:_.message})}let f=h.status;const g=h.headers.get("ETag")||void 0;let E,F;if(h.status===200){let _;try{_=await h.json()}catch(b){throw p.create("fetch-client-parse",{originalErrorMessage:b==null?void 0:b.message})}E=_.entries,F=_.state}if(F==="INSTANCE_STATE_UNSPECIFIED"?f=500:F==="NO_CHANGE"?f=304:(F==="NO_TEMPLATE"||F==="EMPTY_CONFIG")&&(E={}),f!==304&&f!==200)throw p.create("fetch-status",{httpStatus:f});return{status:f,eTag:g,config:E}}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function ma(e,t){return new Promise((n,r)=>{const a=Math.max(t-Date.now(),0),s=setTimeout(n,a);e.addEventListener(()=>{clearTimeout(s),r(p.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function _a(e){if(!(e instanceof y)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class Ca{constructor(t,n){this.client=t,this.storage=n}async fetch(t){const n=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(t,n)}async attemptFetch(t,{throttleEndTimeMillis:n,backoffCount:r}){await ma(t.signal,n);try{const a=await this.client.fetch(t);return await this.storage.deleteThrottleMetadata(),a}catch(a){if(!_a(a))throw a;const s={throttleEndTimeMillis:Date.now()+Q(r),backoffCount:r+1};return await this.storage.setThrottleMetadata(s),this.attemptFetch(t,s)}}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ia=60*1e3,Ea=12*60*60*1e3;class ba{constructor(t,n,r,a,s){this.app=t,this._client=n,this._storageCache=r,this._storage=a,this._logger=s,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:Ia,minimumFetchIntervalMillis:Ea},this.defaultConfig={}}get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function H(e,t){const n=e.target.error||void 0;return p.create(t,{originalErrorMessage:n&&(n==null?void 0:n.message)})}const A="app_namespace_store",wa="firebase_remote_config",Sa=1;function Ta(){return new Promise((e,t)=>{try{const n=indexedDB.open(wa,Sa);n.onerror=r=>{t(H(r,"storage-open"))},n.onsuccess=r=>{e(r.target.result)},n.onupgradeneeded=r=>{const a=r.target.result;switch(r.oldVersion){case 0:a.createObjectStore(A,{keyPath:"compositeKey"})}}}catch(n){t(p.create("storage-open",{originalErrorMessage:n==null?void 0:n.message}))}})}class ya{constructor(t,n,r,a=Ta()){this.appId=t,this.appName=n,this.namespace=r,this.openDbPromise=a}getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(t){return this.set("last_fetch_status",t)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(t){return this.set("last_successful_fetch_timestamp_millis",t)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(t){return this.set("last_successful_fetch_response",t)}getActiveConfig(){return this.get("active_config")}setActiveConfig(t){return this.set("active_config",t)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(t){return this.set("active_config_etag",t)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(t){return this.set("throttle_metadata",t)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}async get(t){const n=await this.openDbPromise;return new Promise((r,a)=>{const i=n.transaction([A],"readonly").objectStore(A),c=this.createCompositeKey(t);try{const o=i.get(c);o.onerror=l=>{a(H(l,"storage-get"))},o.onsuccess=l=>{const d=l.target.result;r(d?d.value:void 0)}}catch(o){a(p.create("storage-get",{originalErrorMessage:o==null?void 0:o.message}))}})}async set(t,n){const r=await this.openDbPromise;return new Promise((a,s)=>{const c=r.transaction([A],"readwrite").objectStore(A),o=this.createCompositeKey(t);try{const l=c.put({compositeKey:o,value:n});l.onerror=d=>{s(H(d,"storage-set"))},l.onsuccess=()=>{a()}}catch(l){s(p.create("storage-set",{originalErrorMessage:l==null?void 0:l.message}))}})}async delete(t){const n=await this.openDbPromise;return new Promise((r,a)=>{const i=n.transaction([A],"readwrite").objectStore(A),c=this.createCompositeKey(t);try{const o=i.delete(c);o.onerror=l=>{a(H(l,"storage-delete"))},o.onsuccess=()=>{r()}}catch(o){a(p.create("storage-delete",{originalErrorMessage:o==null?void 0:o.message}))}})}createCompositeKey(t){return[this.appId,this.appName,this.namespace,t].join()}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Aa{constructor(t){this.storage=t}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}async loadFromStorage(){const t=this.storage.getLastFetchStatus(),n=this.storage.getLastSuccessfulFetchTimestampMillis(),r=this.storage.getActiveConfig(),a=await t;a&&(this.lastFetchStatus=a);const s=await n;s&&(this.lastSuccessfulFetchTimestampMillis=s);const i=await r;i&&(this.activeConfig=i)}setLastFetchStatus(t){return this.lastFetchStatus=t,this.storage.setLastFetchStatus(t)}setLastSuccessfulFetchTimestampMillis(t){return this.lastSuccessfulFetchTimestampMillis=t,this.storage.setLastSuccessfulFetchTimestampMillis(t)}setActiveConfig(t){return this.activeConfig=t,this.storage.setActiveConfig(t)}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Da(){T(new S(ua,e,"PUBLIC").setMultipleInstances(!0)),I(X,Fe),I(X,Fe,"esm2017");function e(t,{instanceIdentifier:n}){const r=t.getProvider("app").getImmediate(),a=t.getProvider("installations-internal").getImmediate();if(typeof window>"u")throw p.create("registration-window");if(!re())throw p.create("indexed-db-unavailable");const{projectId:s,apiKey:i,appId:c}=r.options;if(!s)throw p.create("registration-project-id");if(!i)throw p.create("registration-api-key");if(!c)throw p.create("registration-app-id");n=n||"firebase";const o=new ya(c,r.name,n),l=new Aa(o),d=new ae(X);d.logLevel=u.ERROR;const h=new pa(a,Ln,n,s,i,c),f=new Ca(h,o),g=new fa(f,o,l,d),E=new ba(r,g,l,o,d);return ha(E),E}}Da();const Oa=e=>Object.fromEntries(new URLSearchParams(e)),La=()=>{const e=Et(),t=Oa(e.search);return"utm_campaign"in t&&"utm_medium"in t&&"utm_source"in t?{traffic_campaign:t.utm_campaign,traffic_medium:t.utm_medium,traffic_source:t.utm_source}:{}},Ra=()=>{const e=La();return{logEvent:It.useCallback((n,r)=>{},[e])}};var _t=(e=>(e.CLICKED_BOOKING="hasClickedBooking",e.CLICKED_CANCELED_SELECTED_OFFERS="hasClickedCancelOffers",e.CLICKED_DISABLED_SELECTED_OFFERS="hasClickedDisabledOffers",e.CLICKED_CONSULT_CGU="hasClickedConsultCGU",e.CLICKED_CONSULT_SUPPORT="hasClickedConsultSupport",e.CLICKED_CREATE_ACCOUNT="hasClickedCreateAccount",e.CLICKED_CREATE_VENUE="hasClickedCreateVenue",e.CLICKED_ADD_BANK_INFORMATIONS="hasClickedAddBankInformation",e.CLICKED_NO_PRICING_POINT_SELECTED_YET="hasClickedNoPricingPointSelectedYet",e.CLICKED_ADD_VENUE_IN_OFFERER="hasClickedAddVenueInOfferer",e.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL="hasClickedSeeLaterFromSuccessVenueCreationModal",e.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL="hasClickedSeeLaterFromSuccessOfferCreationModal",e.CLICKED_SAVE_VENUE="hasClickedSaveVenue",e.CLICKED_DOWNLOAD_BOOKINGS="hasClickedDownloadBooking",e.CLICKED_DOWNLOAD_BOOKINGS_CSV="hasClickedDownloadBookingCsv",e.CLICKED_DOWNLOAD_BOOKINGS_OTHER_FORMAT="hasClickedDownloadBookingOtherFormat",e.CLICKED_DOWNLOAD_BOOKINGS_XLS="hasClickedDownloadBookingXls",e.CLICKED_EDIT_PROFILE="hasClickedEditProfile",e.CLICKED_HOME_STATS_PENDING_OFFERS_FAQ="hasClickedHomeStatsPendingOffersFaq",e.CLICKED_FORGOTTEN_PASSWORD="hasClickedForgottenPassword",e.CLICKED_HELP_CENTER="hasClickedHelpCenter",e.CLICKED_HOME="hasClickedHome",e.CLICKED_LOGOUT="hasClickedLogout",e.CLICKED_OFFER="hasClickedOffer",e.CLICKED_OFFER_FORM_NAVIGATION="hasClickedOfferFormNavigation",e.CLICKED_ONBOARDING_FORM_NAVIGATION="HasClickedOnboardingFormNavigation",e.CLICKED_CANCEL_OFFER_CREATION="hasClickedCancelOfferCreation",e.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK="hasClickedPartnerBlockPreviewVenueLink",e.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK="hasClickedPartnerBlockCopyVenueLink",e.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK="hasClickedPartnerBlockDmsApplicationLink",e.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK="hasClickedPartnerBlockCollectiveHelpLink",e.CLICKED_PERSONAL_DATA="hasClickedConsultPersonalData",e.CLICKED_PRO="hasClickedPro",e.CLICKED_REIMBURSEMENT="hasClickedReimbursement",e.CLICKED_SHOW_BOOKINGS="hasClickedShowBooking",e.CLICKED_STATS="hasClickedOffererStats",e.CLICKED_TICKET="hasClickedTicket",e.CLICKED_TOGGLE_HIDE_OFFERER_NAME="hasClickedToggleHideOffererName",e.CLICKED_DUPLICATE_TEMPLATE_OFFER="hasClickedDuplicateTemplateOffer",e.CLICKED_BEST_PRACTICES_STUDIES="hasClickedBestPracticesAndStudies",e.CLICKED_HELP_LINK="hasClickedHelpLink",e.CLICKED_RESET_FILTERS="hasClickedResetFilter",e.CLICKED_SHOW_STATUS_FILTER="hasClickedShowStatusFilter",e.CLICKED_OMNI_SEARCH_CRITERIA="hasClickedOmniSearchCriteria",e.CLICKED_PAGINATION_NEXT_PAGE="hasClickedPaginationNextPage",e.CLICKED_PAGINATION_PREVIOUS_PAGE="hasClickedPaginationPreviousPage",e.CLICKED_CONTACT_OUR_TEAMS="hasClickedContactOurTeams",e.FIRST_LOGIN="firstLogin",e.PAGE_VIEW="page_view",e.SIGNUP_FORM_ABORT="signupFormAbort",e.SIGNUP_FORM_SUCCESS="signupFormSuccess",e.TUTO_PAGE_VIEW="tutoPageView",e.DELETE_DRAFT_OFFER="DeleteDraftOffer",e.CLICKED_NO_VENUE="hasClickedNoVenue",e.CLICKED_EAC_DMS_TIMELINE="hasClickedEacDmsTimeline",e.CLICKED_EAC_DMS_LINK="hasClickedEacDmsLink",e.CLICKED_CREATE_OFFER_FROM_REQUEST="hasClickedCreateOfferFromRequest",e.CLICKED_ADD_IMAGE="hasClickedAddImage",e.CLICKED_DELETE_STOCK="hasClickedDeleteStock",e.CLICKED_BULK_DELETE_STOCK="hasClickedBulkDeleteStock",e.CLICKED_DOWNLOAD_OFFER_BOOKINGS="hasDownloadedBookings",e.CLICKED_PAGE_FOR_APP_HOME="hasClickedPageForAppHome",e.CLICKED_PAGE_FOR_ADAGE_HOME="hasClickedPageForAdageHome",e.CLICKED_INVOICES_DOWNLOAD="hasClickedInvoicesDownload",e.CLICKED_PUBLISH_FUTURE_OFFER_EARLIER="hasClickedPublishFutureOfferEarlier",e))(_t||{});const ke={"help-link":"_help-link_1c4y5_2","help-link-text":"_help-link-text_1c4y5_10"},Fa=()=>{const{logEvent:e}=Ra();return k.jsxs("a",{onClick:()=>e(_t.CLICKED_HELP_LINK,{from:location.pathname}),className:ke["help-link"],href:"https://aide.passculture.app/hc/fr/articles/4411991940369--Acteurs-culturels-Comment-poster-une-offre-%C3%A0-destination-d-un-groupe-scolaire-",rel:"noreferrer",target:"_blank",children:[k.jsx(wt,{src:bt,alt:"",width:"42"}),k.jsx("span",{className:ke["help-link-text"],children:"Aide"})]})},Ua={title:"components/HelpLink",component:Fa,decorators:[e=>k.jsx("div",{style:{width:500,height:500},children:k.jsx(e,{})}),Ct]},K={};var Ne,ve,Me;K.parameters={...K.parameters,docs:{...(Ne=K.parameters)==null?void 0:Ne.docs,source:{originalSource:"{}",...(Me=(ve=K.parameters)==null?void 0:ve.docs)==null?void 0:Me.source}}};const xa=["Default"];export{K as Default,xa as __namedExportsOrder,Ua as default};
