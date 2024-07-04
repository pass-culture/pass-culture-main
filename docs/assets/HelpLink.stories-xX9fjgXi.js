import{j as P}from"./jsx-runtime-X2b_N9AH.js";import{r as dt}from"./index-uCp2LrAq.js";import"./config-yp2pWrHW.js";import{u as ft}from"./index-BsMtPDqD.js";import{f as gt}from"./full-help-Co3hxUDJ.js";import{S as pt}from"./SvgIcon-DP_815J1.js";import"./_commonjsHelpers-BosuxZz1.js";/**
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
 */const Fe=function(e){const t=[];let n=0;for(let r=0;r<e.length;r++){let a=e.charCodeAt(r);a<128?t[n++]=a:a<2048?(t[n++]=a>>6|192,t[n++]=a&63|128):(a&64512)===55296&&r+1<e.length&&(e.charCodeAt(r+1)&64512)===56320?(a=65536+((a&1023)<<10)+(e.charCodeAt(++r)&1023),t[n++]=a>>18|240,t[n++]=a>>12&63|128,t[n++]=a>>6&63|128,t[n++]=a&63|128):(t[n++]=a>>12|224,t[n++]=a>>6&63|128,t[n++]=a&63|128)}return t},mt=function(e){const t=[];let n=0,r=0;for(;n<e.length;){const a=e[n++];if(a<128)t[r++]=String.fromCharCode(a);else if(a>191&&a<224){const s=e[n++];t[r++]=String.fromCharCode((a&31)<<6|s&63)}else if(a>239&&a<365){const s=e[n++],i=e[n++],c=e[n++],o=((a&7)<<18|(s&63)<<12|(i&63)<<6|c&63)-65536;t[r++]=String.fromCharCode(55296+(o>>10)),t[r++]=String.fromCharCode(56320+(o&1023))}else{const s=e[n++],i=e[n++];t[r++]=String.fromCharCode((a&15)<<12|(s&63)<<6|i&63)}}return t.join("")},_t={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(e,t){if(!Array.isArray(e))throw Error("encodeByteArray takes an array as a parameter");this.init_();const n=t?this.byteToCharMapWebSafe_:this.byteToCharMap_,r=[];for(let a=0;a<e.length;a+=3){const s=e[a],i=a+1<e.length,c=i?e[a+1]:0,o=a+2<e.length,l=o?e[a+2]:0,h=s>>2,d=(s&3)<<4|c>>4;let f=(c&15)<<2|l>>6,g=l&63;o||(g=64,i||(f=64)),r.push(n[h],n[d],n[f],n[g])}return r.join("")},encodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?btoa(e):this.encodeByteArray(Fe(e),t)},decodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?atob(e):mt(this.decodeStringToByteArray(e,t))},decodeStringToByteArray(e,t){this.init_();const n=t?this.charToByteMapWebSafe_:this.charToByteMap_,r=[];for(let a=0;a<e.length;){const s=n[e.charAt(a++)],c=a<e.length?n[e.charAt(a)]:0;++a;const l=a<e.length?n[e.charAt(a)]:64;++a;const d=a<e.length?n[e.charAt(a)]:64;if(++a,s==null||c==null||l==null||d==null)throw new Ct;const f=s<<2|c>>4;if(r.push(f),l!==64){const g=c<<4&240|l>>2;if(r.push(g),d!==64){const E=l<<6&192|d;r.push(E)}}}return r},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let e=0;e<this.ENCODED_VALS.length;e++)this.byteToCharMap_[e]=this.ENCODED_VALS.charAt(e),this.charToByteMap_[this.byteToCharMap_[e]]=e,this.byteToCharMapWebSafe_[e]=this.ENCODED_VALS_WEBSAFE.charAt(e),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[e]]=e,e>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(e)]=e,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(e)]=e)}}};class Ct extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const It=function(e){const t=Fe(e);return _t.encodeByteArray(t,!0)},Me=function(e){return It(e).replace(/\./g,"")};function Et(){const e=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof e=="object"&&e.id!==void 0}function ee(){try{return typeof indexedDB=="object"}catch{return!1}}function Ne(){return new Promise((e,t)=>{try{let n=!0;const r="validate-browser-context-for-indexeddb-analytics-module",a=self.indexedDB.open(r);a.onsuccess=()=>{a.result.close(),n||self.indexedDB.deleteDatabase(r),e(!0)},a.onupgradeneeded=()=>{n=!1},a.onerror=()=>{var s;t(((s=a.error)===null||s===void 0?void 0:s.message)||"")}}catch(n){t(n)}})}function bt(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
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
 */const wt="FirebaseError";class y extends Error{constructor(t,n,r){super(n),this.code=t,this.customData=r,this.name=wt,Object.setPrototypeOf(this,y.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,N.prototype.create)}}class N{constructor(t,n,r){this.service=t,this.serviceName=n,this.errors=r}create(t,...n){const r=n[0]||{},a=`${this.service}/${t}`,s=this.errors[t],i=s?St(s,r):"Error",c=`${this.serviceName}: ${i} (${a}).`;return new y(a,c,r)}}function St(e,t){return e.replace(Tt,(n,r)=>{const a=t[r];return a!=null?String(a):`<${r}?>`})}const Tt=/\{\$([^}]+)}/g;/**
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
 */const yt=1e3,At=2,Dt=4*60*60*1e3,Ot=.5;function Y(e,t=yt,n=At){const r=t*Math.pow(n,e),a=Math.round(Ot*r*(Math.random()-.5)*2);return Math.min(Dt,r+a)}/**
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
 */function ve(e){return e&&e._delegate?e._delegate:e}class S{constructor(t,n,r){this.name=t,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}}/**
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
 */var u;(function(e){e[e.DEBUG=0]="DEBUG",e[e.VERBOSE=1]="VERBOSE",e[e.INFO=2]="INFO",e[e.WARN=3]="WARN",e[e.ERROR=4]="ERROR",e[e.SILENT=5]="SILENT"})(u||(u={}));const Lt={debug:u.DEBUG,verbose:u.VERBOSE,info:u.INFO,warn:u.WARN,error:u.ERROR,silent:u.SILENT},Rt=u.INFO,kt={[u.DEBUG]:"log",[u.VERBOSE]:"log",[u.INFO]:"info",[u.WARN]:"warn",[u.ERROR]:"error"},Pt=(e,t,...n)=>{if(t<e.logLevel)return;const r=new Date().toISOString(),a=kt[t];if(a)console[a](`[${r}]  ${e.name}:`,...n);else throw new Error(`Attempted to log a message with an invalid logType (value: ${t})`)};class te{constructor(t){this.name=t,this._logLevel=Rt,this._logHandler=Pt,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(t){if(!(t in u))throw new TypeError(`Invalid value "${t}" assigned to \`logLevel\``);this._logLevel=t}setLogLevel(t){this._logLevel=typeof t=="string"?Lt[t]:t}get logHandler(){return this._logHandler}set logHandler(t){if(typeof t!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=t}get userLogHandler(){return this._userLogHandler}set userLogHandler(t){this._userLogHandler=t}debug(...t){this._userLogHandler&&this._userLogHandler(this,u.DEBUG,...t),this._logHandler(this,u.DEBUG,...t)}log(...t){this._userLogHandler&&this._userLogHandler(this,u.VERBOSE,...t),this._logHandler(this,u.VERBOSE,...t)}info(...t){this._userLogHandler&&this._userLogHandler(this,u.INFO,...t),this._logHandler(this,u.INFO,...t)}warn(...t){this._userLogHandler&&this._userLogHandler(this,u.WARN,...t),this._logHandler(this,u.WARN,...t)}error(...t){this._userLogHandler&&this._userLogHandler(this,u.ERROR,...t),this._logHandler(this,u.ERROR,...t)}}const Ft=(e,t)=>t.some(n=>e instanceof n);let ue,he;function Mt(){return ue||(ue=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function Nt(){return he||(he=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const Be=new WeakMap,J=new WeakMap,$e=new WeakMap,x=new WeakMap,ne=new WeakMap;function vt(e){const t=new Promise((n,r)=>{const a=()=>{e.removeEventListener("success",s),e.removeEventListener("error",i)},s=()=>{n(w(e.result)),a()},i=()=>{r(e.error),a()};e.addEventListener("success",s),e.addEventListener("error",i)});return t.then(n=>{n instanceof IDBCursor&&Be.set(n,e)}).catch(()=>{}),ne.set(t,e),t}function Bt(e){if(J.has(e))return;const t=new Promise((n,r)=>{const a=()=>{e.removeEventListener("complete",s),e.removeEventListener("error",i),e.removeEventListener("abort",i)},s=()=>{n(),a()},i=()=>{r(e.error||new DOMException("AbortError","AbortError")),a()};e.addEventListener("complete",s),e.addEventListener("error",i),e.addEventListener("abort",i)});J.set(e,t)}let X={get(e,t,n){if(e instanceof IDBTransaction){if(t==="done")return J.get(e);if(t==="objectStoreNames")return e.objectStoreNames||$e.get(e);if(t==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return w(e[t])},set(e,t,n){return e[t]=n,!0},has(e,t){return e instanceof IDBTransaction&&(t==="done"||t==="store")?!0:t in e}};function $t(e){X=e(X)}function Kt(e){return e===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(t,...n){const r=e.call(U(this),t,...n);return $e.set(r,t.sort?t.sort():[t]),w(r)}:Nt().includes(e)?function(...t){return e.apply(U(this),t),w(Be.get(this))}:function(...t){return w(e.apply(U(this),t))}}function Ht(e){return typeof e=="function"?Kt(e):(e instanceof IDBTransaction&&Bt(e),Ft(e,Mt())?new Proxy(e,X):e)}function w(e){if(e instanceof IDBRequest)return vt(e);if(x.has(e))return x.get(e);const t=Ht(e);return t!==e&&(x.set(e,t),ne.set(t,e)),t}const U=e=>ne.get(e);function Ke(e,t,{blocked:n,upgrade:r,blocking:a,terminated:s}={}){const i=indexedDB.open(e,t),c=w(i);return r&&i.addEventListener("upgradeneeded",o=>{r(w(i.result),o.oldVersion,o.newVersion,w(i.transaction),o)}),n&&i.addEventListener("blocked",o=>n(o.oldVersion,o.newVersion,o)),c.then(o=>{s&&o.addEventListener("close",()=>s()),a&&o.addEventListener("versionchange",l=>a(l.oldVersion,l.newVersion,l))}).catch(()=>{}),c}const xt=["get","getKey","getAll","getAllKeys","count"],Ut=["put","add","delete","clear"],V=new Map;function de(e,t){if(!(e instanceof IDBDatabase&&!(t in e)&&typeof t=="string"))return;if(V.get(t))return V.get(t);const n=t.replace(/FromIndex$/,""),r=t!==n,a=Ut.includes(n);if(!(n in(r?IDBIndex:IDBObjectStore).prototype)||!(a||xt.includes(n)))return;const s=async function(i,...c){const o=this.transaction(i,a?"readwrite":"readonly");let l=o.store;return r&&(l=l.index(c.shift())),(await Promise.all([l[n](...c),a&&o.done]))[0]};return V.set(t,s),s}$t(e=>({...e,get:(t,n,r)=>de(t,n)||e.get(t,n,r),has:(t,n)=>!!de(t,n)||e.has(t,n)}));/**
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
 */class Vt{constructor(t){this.container=t}getPlatformInfoString(){return this.container.getProviders().map(n=>{if(jt(n)){const r=n.getImmediate();return`${r.library}/${r.version}`}else return null}).filter(n=>n).join(" ")}}function jt(e){const t=e.getComponent();return(t==null?void 0:t.type)==="VERSION"}const Q="@firebase/app",fe="0.10.6";/**
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
 */const O=new te("@firebase/app"),Gt="@firebase/app-compat",Wt="@firebase/analytics-compat",qt="@firebase/analytics",zt="@firebase/app-check-compat",Yt="@firebase/app-check",Jt="@firebase/auth",Xt="@firebase/auth-compat",Qt="@firebase/database",Zt="@firebase/database-compat",en="@firebase/functions",tn="@firebase/functions-compat",nn="@firebase/installations",rn="@firebase/installations-compat",an="@firebase/messaging",sn="@firebase/messaging-compat",on="@firebase/performance",cn="@firebase/performance-compat",ln="@firebase/remote-config",un="@firebase/remote-config-compat",hn="@firebase/storage",dn="@firebase/storage-compat",fn="@firebase/firestore",gn="@firebase/vertexai-preview",pn="@firebase/firestore-compat",mn="firebase",_n="10.12.3",Cn={[Q]:"fire-core",[Gt]:"fire-core-compat",[qt]:"fire-analytics",[Wt]:"fire-analytics-compat",[Yt]:"fire-app-check",[zt]:"fire-app-check-compat",[Jt]:"fire-auth",[Xt]:"fire-auth-compat",[Qt]:"fire-rtdb",[Zt]:"fire-rtdb-compat",[en]:"fire-fn",[tn]:"fire-fn-compat",[nn]:"fire-iid",[rn]:"fire-iid-compat",[an]:"fire-fcm",[sn]:"fire-fcm-compat",[on]:"fire-perf",[cn]:"fire-perf-compat",[ln]:"fire-rc",[un]:"fire-rc-compat",[hn]:"fire-gcs",[dn]:"fire-gcs-compat",[fn]:"fire-fst",[pn]:"fire-fst-compat",[gn]:"fire-vertex","fire-js":"fire-js",[mn]:"fire-js-all"};/**
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
 */const In=new Map,En=new Map,ge=new Map;function pe(e,t){try{e.container.addComponent(t)}catch(n){O.debug(`Component ${t.name} failed to register with FirebaseApp ${e.name}`,n)}}function T(e){const t=e.name;if(ge.has(t))return O.debug(`There were multiple attempts to register component ${t}.`),!1;ge.set(t,e);for(const n of In.values())pe(n,e);for(const n of En.values())pe(n,e);return!0}function He(e,t){const n=e.container.getProvider("heartbeat").getImmediate({optional:!0});return n&&n.triggerHeartbeat(),e.container.getProvider(t)}/**
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
 */const bn={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},re=new N("app","Firebase",bn);/**
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
 */const wn=_n;function I(e,t,n){var r;let a=(r=Cn[e])!==null&&r!==void 0?r:e;n&&(a+=`-${n}`);const s=a.match(/\s|\//),i=t.match(/\s|\//);if(s||i){const c=[`Unable to register library "${a}" with version "${t}":`];s&&c.push(`library name "${a}" contains illegal characters (whitespace or "/")`),s&&i&&c.push("and"),i&&c.push(`version name "${t}" contains illegal characters (whitespace or "/")`),O.warn(c.join(" "));return}T(new S(`${a}-version`,()=>({library:a,version:t}),"VERSION"))}/**
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
 */const Sn="firebase-heartbeat-database",Tn=1,M="firebase-heartbeat-store";let j=null;function xe(){return j||(j=Ke(Sn,Tn,{upgrade:(e,t)=>{switch(t){case 0:try{e.createObjectStore(M)}catch(n){console.warn(n)}}}}).catch(e=>{throw re.create("idb-open",{originalErrorMessage:e.message})})),j}async function yn(e){try{const n=(await xe()).transaction(M),r=await n.objectStore(M).get(Ue(e));return await n.done,r}catch(t){if(t instanceof y)O.warn(t.message);else{const n=re.create("idb-get",{originalErrorMessage:t==null?void 0:t.message});O.warn(n.message)}}}async function me(e,t){try{const r=(await xe()).transaction(M,"readwrite");await r.objectStore(M).put(t,Ue(e)),await r.done}catch(n){if(n instanceof y)O.warn(n.message);else{const r=re.create("idb-set",{originalErrorMessage:n==null?void 0:n.message});O.warn(r.message)}}}function Ue(e){return`${e.name}!${e.options.appId}`}/**
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
 */const An=1024,Dn=30*24*60*60*1e3;class On{constructor(t){this.container=t,this._heartbeatsCache=null;const n=this.container.getProvider("app").getImmediate();this._storage=new Rn(n),this._heartbeatsCachePromise=this._storage.read().then(r=>(this._heartbeatsCache=r,r))}async triggerHeartbeat(){var t,n;const a=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),s=_e();if(!(((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,((n=this._heartbeatsCache)===null||n===void 0?void 0:n.heartbeats)==null))&&!(this._heartbeatsCache.lastSentHeartbeatDate===s||this._heartbeatsCache.heartbeats.some(i=>i.date===s)))return this._heartbeatsCache.heartbeats.push({date:s,agent:a}),this._heartbeatsCache.heartbeats=this._heartbeatsCache.heartbeats.filter(i=>{const c=new Date(i.date).valueOf();return Date.now()-c<=Dn}),this._storage.overwrite(this._heartbeatsCache)}async getHeartbeatsHeader(){var t;if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null||this._heartbeatsCache.heartbeats.length===0)return"";const n=_e(),{heartbeatsToSend:r,unsentEntries:a}=Ln(this._heartbeatsCache.heartbeats),s=Me(JSON.stringify({version:2,heartbeats:r}));return this._heartbeatsCache.lastSentHeartbeatDate=n,a.length>0?(this._heartbeatsCache.heartbeats=a,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),s}}function _e(){return new Date().toISOString().substring(0,10)}function Ln(e,t=An){const n=[];let r=e.slice();for(const a of e){const s=n.find(i=>i.agent===a.agent);if(s){if(s.dates.push(a.date),Ce(n)>t){s.dates.pop();break}}else if(n.push({agent:a.agent,dates:[a.date]}),Ce(n)>t){n.pop();break}r=r.slice(1)}return{heartbeatsToSend:n,unsentEntries:r}}class Rn{constructor(t){this.app=t,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return ee()?Ne().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const n=await yn(this.app);return n!=null&&n.heartbeats?n:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(t){var n;if(await this._canUseIndexedDBPromise){const a=await this.read();return me(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:a.lastSentHeartbeatDate,heartbeats:t.heartbeats})}else return}async add(t){var n;if(await this._canUseIndexedDBPromise){const a=await this.read();return me(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:a.lastSentHeartbeatDate,heartbeats:[...a.heartbeats,...t.heartbeats]})}else return}}function Ce(e){return Me(JSON.stringify({version:2,heartbeats:e})).length}/**
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
 */function kn(e){T(new S("platform-logger",t=>new Vt(t),"PRIVATE")),T(new S("heartbeat",t=>new On(t),"PRIVATE")),I(Q,fe,e),I(Q,fe,"esm2017"),I("fire-js","")}kn("");const Ve="@firebase/installations",ae="0.6.8";/**
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
 */const je=1e4,Ge=`w:${ae}`,We="FIS_v2",Pn="https://firebaseinstallations.googleapis.com/v1",Fn=60*60*1e3,Mn="installations",Nn="Installations";/**
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
 */const vn={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},L=new N(Mn,Nn,vn);function qe(e){return e instanceof y&&e.code.includes("request-failed")}/**
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
 */function ze({projectId:e}){return`${Pn}/projects/${e}/installations`}function Ye(e){return{token:e.token,requestStatus:2,expiresIn:$n(e.expiresIn),creationTime:Date.now()}}async function Je(e,t){const r=(await t.json()).error;return L.create("request-failed",{requestName:e,serverCode:r.code,serverMessage:r.message,serverStatus:r.status})}function Xe({apiKey:e}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e})}function Bn(e,{refreshToken:t}){const n=Xe(e);return n.append("Authorization",Kn(t)),n}async function Qe(e){const t=await e();return t.status>=500&&t.status<600?e():t}function $n(e){return Number(e.replace("s","000"))}function Kn(e){return`${We} ${e}`}/**
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
 */async function Hn({appConfig:e,heartbeatServiceProvider:t},{fid:n}){const r=ze(e),a=Xe(e),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&a.append("x-firebase-client",l)}const i={fid:n,authVersion:We,appId:e.appId,sdkVersion:Ge},c={method:"POST",headers:a,body:JSON.stringify(i)},o=await Qe(()=>fetch(r,c));if(o.ok){const l=await o.json();return{fid:l.fid||n,registrationStatus:2,refreshToken:l.refreshToken,authToken:Ye(l.authToken)}}else throw await Je("Create Installation",o)}/**
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
 */function Ze(e){return new Promise(t=>{setTimeout(t,e)})}/**
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
 */function xn(e){return btoa(String.fromCharCode(...e)).replace(/\+/g,"-").replace(/\//g,"_")}/**
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
 */const Un=/^[cdef][\w-]{21}$/,Z="";function Vn(){try{const e=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(e),e[0]=112+e[0]%16;const n=jn(e);return Un.test(n)?n:Z}catch{return Z}}function jn(e){return xn(e).substr(0,22)}/**
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
 */function K(e){return`${e.appName}!${e.appId}`}/**
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
 */const et=new Map;function tt(e,t){const n=K(e);nt(n,t),Gn(n,t)}function nt(e,t){const n=et.get(e);if(n)for(const r of n)r(t)}function Gn(e,t){const n=Wn();n&&n.postMessage({key:e,fid:t}),qn()}let D=null;function Wn(){return!D&&"BroadcastChannel"in self&&(D=new BroadcastChannel("[Firebase] FID Change"),D.onmessage=e=>{nt(e.data.key,e.data.fid)}),D}function qn(){et.size===0&&D&&(D.close(),D=null)}/**
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
 */const zn="firebase-installations-database",Yn=1,R="firebase-installations-store";let G=null;function se(){return G||(G=Ke(zn,Yn,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(R)}}})),G}async function $(e,t){const n=K(e),a=(await se()).transaction(R,"readwrite"),s=a.objectStore(R),i=await s.get(n);return await s.put(t,n),await a.done,(!i||i.fid!==t.fid)&&tt(e,t.fid),t}async function rt(e){const t=K(e),r=(await se()).transaction(R,"readwrite");await r.objectStore(R).delete(t),await r.done}async function H(e,t){const n=K(e),a=(await se()).transaction(R,"readwrite"),s=a.objectStore(R),i=await s.get(n),c=t(i);return c===void 0?await s.delete(n):await s.put(c,n),await a.done,c&&(!i||i.fid!==c.fid)&&tt(e,c.fid),c}/**
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
 */async function ie(e){let t;const n=await H(e.appConfig,r=>{const a=Jn(r),s=Xn(e,a);return t=s.registrationPromise,s.installationEntry});return n.fid===Z?{installationEntry:await t}:{installationEntry:n,registrationPromise:t}}function Jn(e){const t=e||{fid:Vn(),registrationStatus:0};return at(t)}function Xn(e,t){if(t.registrationStatus===0){if(!navigator.onLine){const a=Promise.reject(L.create("app-offline"));return{installationEntry:t,registrationPromise:a}}const n={fid:t.fid,registrationStatus:1,registrationTime:Date.now()},r=Qn(e,n);return{installationEntry:n,registrationPromise:r}}else return t.registrationStatus===1?{installationEntry:t,registrationPromise:Zn(e)}:{installationEntry:t}}async function Qn(e,t){try{const n=await Hn(e,t);return $(e.appConfig,n)}catch(n){throw qe(n)&&n.customData.serverCode===409?await rt(e.appConfig):await $(e.appConfig,{fid:t.fid,registrationStatus:0}),n}}async function Zn(e){let t=await Ie(e.appConfig);for(;t.registrationStatus===1;)await Ze(100),t=await Ie(e.appConfig);if(t.registrationStatus===0){const{installationEntry:n,registrationPromise:r}=await ie(e);return r||n}return t}function Ie(e){return H(e,t=>{if(!t)throw L.create("installation-not-found");return at(t)})}function at(e){return er(e)?{fid:e.fid,registrationStatus:0}:e}function er(e){return e.registrationStatus===1&&e.registrationTime+je<Date.now()}/**
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
 */async function tr({appConfig:e,heartbeatServiceProvider:t},n){const r=nr(e,n),a=Bn(e,n),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&a.append("x-firebase-client",l)}const i={installation:{sdkVersion:Ge,appId:e.appId}},c={method:"POST",headers:a,body:JSON.stringify(i)},o=await Qe(()=>fetch(r,c));if(o.ok){const l=await o.json();return Ye(l)}else throw await Je("Generate Auth Token",o)}function nr(e,{fid:t}){return`${ze(e)}/${t}/authTokens:generate`}/**
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
 */async function oe(e,t=!1){let n;const r=await H(e.appConfig,s=>{if(!st(s))throw L.create("not-registered");const i=s.authToken;if(!t&&sr(i))return s;if(i.requestStatus===1)return n=rr(e,t),s;{if(!navigator.onLine)throw L.create("app-offline");const c=or(s);return n=ar(e,c),c}});return n?await n:r.authToken}async function rr(e,t){let n=await Ee(e.appConfig);for(;n.authToken.requestStatus===1;)await Ze(100),n=await Ee(e.appConfig);const r=n.authToken;return r.requestStatus===0?oe(e,t):r}function Ee(e){return H(e,t=>{if(!st(t))throw L.create("not-registered");const n=t.authToken;return cr(n)?Object.assign(Object.assign({},t),{authToken:{requestStatus:0}}):t})}async function ar(e,t){try{const n=await tr(e,t),r=Object.assign(Object.assign({},t),{authToken:n});return await $(e.appConfig,r),n}catch(n){if(qe(n)&&(n.customData.serverCode===401||n.customData.serverCode===404))await rt(e.appConfig);else{const r=Object.assign(Object.assign({},t),{authToken:{requestStatus:0}});await $(e.appConfig,r)}throw n}}function st(e){return e!==void 0&&e.registrationStatus===2}function sr(e){return e.requestStatus===2&&!ir(e)}function ir(e){const t=Date.now();return t<e.creationTime||e.creationTime+e.expiresIn<t+Fn}function or(e){const t={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},e),{authToken:t})}function cr(e){return e.requestStatus===1&&e.requestTime+je<Date.now()}/**
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
 */async function lr(e){const t=e,{installationEntry:n,registrationPromise:r}=await ie(t);return r?r.catch(console.error):oe(t).catch(console.error),n.fid}/**
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
 */async function ur(e,t=!1){const n=e;return await hr(n),(await oe(n,t)).token}async function hr(e){const{registrationPromise:t}=await ie(e);t&&await t}/**
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
 */function dr(e){if(!e||!e.options)throw W("App Configuration");if(!e.name)throw W("App Name");const t=["projectId","apiKey","appId"];for(const n of t)if(!e.options[n])throw W(n);return{appName:e.name,projectId:e.options.projectId,apiKey:e.options.apiKey,appId:e.options.appId}}function W(e){return L.create("missing-app-config-values",{valueName:e})}/**
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
 */const it="installations",fr="installations-internal",gr=e=>{const t=e.getProvider("app").getImmediate(),n=dr(t),r=He(t,"heartbeat");return{app:t,appConfig:n,heartbeatServiceProvider:r,_delete:()=>Promise.resolve()}},pr=e=>{const t=e.getProvider("app").getImmediate(),n=He(t,it).getImmediate();return{getId:()=>lr(n),getToken:a=>ur(n,a)}};function mr(){T(new S(it,gr,"PUBLIC")),T(new S(fr,pr,"PRIVATE"))}mr();I(Ve,ae);I(Ve,ae,"esm2017");/**
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
 */const be="analytics",_r="firebase_id",Cr="origin",Ir=60*1e3,Er="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",ce="https://www.googletagmanager.com/gtag/js";/**
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
 */const m=new te("@firebase/analytics");/**
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
 */const br={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-intialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},_=new N("analytics","Analytics",br);/**
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
 */function wr(e){if(!e.startsWith(ce)){const t=_.create("invalid-gtag-resource",{gtagURL:e});return m.warn(t.message),""}return e}function ot(e){return Promise.all(e.map(t=>t.catch(n=>n)))}function Sr(e,t){let n;return window.trustedTypes&&(n=window.trustedTypes.createPolicy(e,t)),n}function Tr(e,t){const n=Sr("firebase-js-sdk-policy",{createScriptURL:wr}),r=document.createElement("script"),a=`${ce}?l=${e}&id=${t}`;r.src=n?n==null?void 0:n.createScriptURL(a):a,r.async=!0,document.head.appendChild(r)}function yr(e){let t=[];return Array.isArray(window[e])?t=window[e]:window[e]=t,t}async function Ar(e,t,n,r,a,s){const i=r[a];try{if(i)await t[i];else{const o=(await ot(n)).find(l=>l.measurementId===a);o&&await t[o.appId]}}catch(c){m.error(c)}e("config",a,s)}async function Dr(e,t,n,r,a){try{let s=[];if(a&&a.send_to){let i=a.send_to;Array.isArray(i)||(i=[i]);const c=await ot(n);for(const o of i){const l=c.find(d=>d.measurementId===o),h=l&&t[l.appId];if(h)s.push(h);else{s=[];break}}}s.length===0&&(s=Object.values(t)),await Promise.all(s),e("event",r,a||{})}catch(s){m.error(s)}}function Or(e,t,n,r){async function a(s,...i){try{if(s==="event"){const[c,o]=i;await Dr(e,t,n,c,o)}else if(s==="config"){const[c,o]=i;await Ar(e,t,n,r,c,o)}else if(s==="consent"){const[c,o]=i;e("consent",c,o)}else if(s==="get"){const[c,o,l]=i;e("get",c,o,l)}else if(s==="set"){const[c]=i;e("set",c)}else e(s,...i)}catch(c){m.error(c)}}return a}function Lr(e,t,n,r,a){let s=function(...i){window[r].push(arguments)};return window[a]&&typeof window[a]=="function"&&(s=window[a]),window[a]=Or(s,e,t,n),{gtagCore:s,wrappedGtag:window[a]}}function Rr(e){const t=window.document.getElementsByTagName("script");for(const n of Object.values(t))if(n.src&&n.src.includes(ce)&&n.src.includes(e))return n;return null}/**
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
 */const kr=30,Pr=1e3;class Fr{constructor(t={},n=Pr){this.throttleMetadata=t,this.intervalMillis=n}getThrottleMetadata(t){return this.throttleMetadata[t]}setThrottleMetadata(t,n){this.throttleMetadata[t]=n}deleteThrottleMetadata(t){delete this.throttleMetadata[t]}}const ct=new Fr;function Mr(e){return new Headers({Accept:"application/json","x-goog-api-key":e})}async function Nr(e){var t;const{appId:n,apiKey:r}=e,a={method:"GET",headers:Mr(r)},s=Er.replace("{app-id}",n),i=await fetch(s,a);if(i.status!==200&&i.status!==304){let c="";try{const o=await i.json();!((t=o.error)===null||t===void 0)&&t.message&&(c=o.error.message)}catch{}throw _.create("config-fetch-failed",{httpStatus:i.status,responseMessage:c})}return i.json()}async function vr(e,t=ct,n){const{appId:r,apiKey:a,measurementId:s}=e.options;if(!r)throw _.create("no-app-id");if(!a){if(s)return{measurementId:s,appId:r};throw _.create("no-api-key")}const i=t.getThrottleMetadata(r)||{backoffCount:0,throttleEndTimeMillis:Date.now()},c=new Kr;return setTimeout(async()=>{c.abort()},n!==void 0?n:Ir),lt({appId:r,apiKey:a,measurementId:s},i,c,t)}async function lt(e,{throttleEndTimeMillis:t,backoffCount:n},r,a=ct){var s;const{appId:i,measurementId:c}=e;try{await Br(r,t)}catch(o){if(c)return m.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${c} provided in the "measurementId" field in the local Firebase config. [${o==null?void 0:o.message}]`),{appId:i,measurementId:c};throw o}try{const o=await Nr(e);return a.deleteThrottleMetadata(i),o}catch(o){const l=o;if(!$r(l)){if(a.deleteThrottleMetadata(i),c)return m.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${c} provided in the "measurementId" field in the local Firebase config. [${l==null?void 0:l.message}]`),{appId:i,measurementId:c};throw o}const h=Number((s=l==null?void 0:l.customData)===null||s===void 0?void 0:s.httpStatus)===503?Y(n,a.intervalMillis,kr):Y(n,a.intervalMillis),d={throttleEndTimeMillis:Date.now()+h,backoffCount:n+1};return a.setThrottleMetadata(i,d),m.debug(`Calling attemptFetch again in ${h} millis`),lt(e,d,r,a)}}function Br(e,t){return new Promise((n,r)=>{const a=Math.max(t-Date.now(),0),s=setTimeout(n,a);e.addEventListener(()=>{clearTimeout(s),r(_.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function $r(e){if(!(e instanceof y)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class Kr{constructor(){this.listeners=[]}addEventListener(t){this.listeners.push(t)}abort(){this.listeners.forEach(t=>t())}}async function Hr(e,t,n,r,a){if(a&&a.global){e("event",n,r);return}else{const s=await t,i=Object.assign(Object.assign({},r),{send_to:s});e("event",n,i)}}/**
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
 */async function xr(){if(ee())try{await Ne()}catch(e){return m.warn(_.create("indexeddb-unavailable",{errorInfo:e==null?void 0:e.toString()}).message),!1}else return m.warn(_.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function Ur(e,t,n,r,a,s,i){var c;const o=vr(e);o.then(g=>{n[g.measurementId]=g.appId,e.options.measurementId&&g.measurementId!==e.options.measurementId&&m.warn(`The measurement ID in the local Firebase config (${e.options.measurementId}) does not match the measurement ID fetched from the server (${g.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(g=>m.error(g)),t.push(o);const l=xr().then(g=>{if(g)return r.getId()}),[h,d]=await Promise.all([o,l]);Rr(s)||Tr(s,h.measurementId),a("js",new Date);const f=(c=i==null?void 0:i.config)!==null&&c!==void 0?c:{};return f[Cr]="firebase",f.update=!0,d!=null&&(f[_r]=d),a("config",h.measurementId,f),h.measurementId}/**
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
 */class Vr{constructor(t){this.app=t}_delete(){return delete F[this.app.options.appId],Promise.resolve()}}let F={},we=[];const Se={};let q="dataLayer",jr="gtag",Te,ut,ye=!1;function Gr(){const e=[];if(Et()&&e.push("This is a browser extension environment."),bt()||e.push("Cookies are not available."),e.length>0){const t=e.map((r,a)=>`(${a+1}) ${r}`).join(" "),n=_.create("invalid-analytics-context",{errorInfo:t});m.warn(n.message)}}function Wr(e,t,n){Gr();const r=e.options.appId;if(!r)throw _.create("no-app-id");if(!e.options.apiKey)if(e.options.measurementId)m.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${e.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw _.create("no-api-key");if(F[r]!=null)throw _.create("already-exists",{id:r});if(!ye){yr(q);const{wrappedGtag:s,gtagCore:i}=Lr(F,we,Se,q,jr);ut=s,Te=i,ye=!0}return F[r]=Ur(e,we,Se,t,Te,q,n),new Vr(e)}function qr(e,t,n,r){e=ve(e),Hr(ut,F[e.app.options.appId],t,n,r).catch(a=>m.error(a))}const Ae="@firebase/analytics",De="0.10.5";function zr(){T(new S(be,(t,{options:n})=>{const r=t.getProvider("app").getImmediate(),a=t.getProvider("installations-internal").getImmediate();return Wr(r,a,n)},"PUBLIC")),T(new S("analytics-internal",e,"PRIVATE")),I(Ae,De),I(Ae,De,"esm2017");function e(t){try{const n=t.getProvider(be).getImmediate();return{logEvent:(r,a,s)=>qr(n,r,a,s)}}catch(n){throw _.create("interop-component-reg-failed",{reason:n})}}}zr();const z="@firebase/remote-config",Oe="0.4.8";/**
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
 */const Yr="remote-config";/**
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
 */const Jr={"registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser"},p=new N("remoteconfig","Remote Config",Jr);function Xr(e){const t=ve(e);return t._initializePromise||(t._initializePromise=t._storageCache.loadFromStorage().then(()=>{t._isInitializationComplete=!0})),t._initializePromise}/**
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
 */class Qr{constructor(t,n,r,a){this.client=t,this.storage=n,this.storageCache=r,this.logger=a}isCachedDataFresh(t,n){if(!n)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const r=Date.now()-n,a=r<=t;return this.logger.debug(`Config fetch cache check. Cache age millis: ${r}. Cache max age millis (minimumFetchIntervalMillis setting): ${t}. Is cache hit: ${a}.`),a}async fetch(t){const[n,r]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(r&&this.isCachedDataFresh(t.cacheMaxAgeMillis,n))return r;t.eTag=r&&r.eTag;const a=await this.client.fetch(t),s=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return a.status===200&&s.push(this.storage.setLastSuccessfulFetchResponse(a)),await Promise.all(s),a}}/**
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
 */function Zr(e=navigator){return e.languages&&e.languages[0]||e.language}/**
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
 */class ea{constructor(t,n,r,a,s,i){this.firebaseInstallations=t,this.sdkVersion=n,this.namespace=r,this.projectId=a,this.apiKey=s,this.appId=i}async fetch(t){const[n,r]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),s=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,i={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":t.eTag||"*"},c={sdk_version:this.sdkVersion,app_instance_id:n,app_instance_id_token:r,app_id:this.appId,language_code:Zr()},o={method:"POST",headers:i,body:JSON.stringify(c)},l=fetch(s,o),h=new Promise((C,b)=>{t.signal.addEventListener(()=>{const le=new Error("The operation was aborted.");le.name="AbortError",b(le)})});let d;try{await Promise.race([l,h]),d=await l}catch(C){let b="fetch-client-network";throw(C==null?void 0:C.name)==="AbortError"&&(b="fetch-timeout"),p.create(b,{originalErrorMessage:C==null?void 0:C.message})}let f=d.status;const g=d.headers.get("ETag")||void 0;let E,k;if(d.status===200){let C;try{C=await d.json()}catch(b){throw p.create("fetch-client-parse",{originalErrorMessage:b==null?void 0:b.message})}E=C.entries,k=C.state}if(k==="INSTANCE_STATE_UNSPECIFIED"?f=500:k==="NO_CHANGE"?f=304:(k==="NO_TEMPLATE"||k==="EMPTY_CONFIG")&&(E={}),f!==304&&f!==200)throw p.create("fetch-status",{httpStatus:f});return{status:f,eTag:g,config:E}}}/**
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
 */function ta(e,t){return new Promise((n,r)=>{const a=Math.max(t-Date.now(),0),s=setTimeout(n,a);e.addEventListener(()=>{clearTimeout(s),r(p.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function na(e){if(!(e instanceof y)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class ra{constructor(t,n){this.client=t,this.storage=n}async fetch(t){const n=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(t,n)}async attemptFetch(t,{throttleEndTimeMillis:n,backoffCount:r}){await ta(t.signal,n);try{const a=await this.client.fetch(t);return await this.storage.deleteThrottleMetadata(),a}catch(a){if(!na(a))throw a;const s={throttleEndTimeMillis:Date.now()+Y(r),backoffCount:r+1};return await this.storage.setThrottleMetadata(s),this.attemptFetch(t,s)}}}/**
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
 */const aa=60*1e3,sa=12*60*60*1e3;class ia{constructor(t,n,r,a,s){this.app=t,this._client=n,this._storageCache=r,this._storage=a,this._logger=s,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:aa,minimumFetchIntervalMillis:sa},this.defaultConfig={}}get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}}/**
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
 */function B(e,t){const n=e.target.error||void 0;return p.create(t,{originalErrorMessage:n&&(n==null?void 0:n.message)})}const A="app_namespace_store",oa="firebase_remote_config",ca=1;function la(){return new Promise((e,t)=>{try{const n=indexedDB.open(oa,ca);n.onerror=r=>{t(B(r,"storage-open"))},n.onsuccess=r=>{e(r.target.result)},n.onupgradeneeded=r=>{const a=r.target.result;switch(r.oldVersion){case 0:a.createObjectStore(A,{keyPath:"compositeKey"})}}}catch(n){t(p.create("storage-open",{originalErrorMessage:n==null?void 0:n.message}))}})}class ua{constructor(t,n,r,a=la()){this.appId=t,this.appName=n,this.namespace=r,this.openDbPromise=a}getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(t){return this.set("last_fetch_status",t)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(t){return this.set("last_successful_fetch_timestamp_millis",t)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(t){return this.set("last_successful_fetch_response",t)}getActiveConfig(){return this.get("active_config")}setActiveConfig(t){return this.set("active_config",t)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(t){return this.set("active_config_etag",t)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(t){return this.set("throttle_metadata",t)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}async get(t){const n=await this.openDbPromise;return new Promise((r,a)=>{const i=n.transaction([A],"readonly").objectStore(A),c=this.createCompositeKey(t);try{const o=i.get(c);o.onerror=l=>{a(B(l,"storage-get"))},o.onsuccess=l=>{const h=l.target.result;r(h?h.value:void 0)}}catch(o){a(p.create("storage-get",{originalErrorMessage:o==null?void 0:o.message}))}})}async set(t,n){const r=await this.openDbPromise;return new Promise((a,s)=>{const c=r.transaction([A],"readwrite").objectStore(A),o=this.createCompositeKey(t);try{const l=c.put({compositeKey:o,value:n});l.onerror=h=>{s(B(h,"storage-set"))},l.onsuccess=()=>{a()}}catch(l){s(p.create("storage-set",{originalErrorMessage:l==null?void 0:l.message}))}})}async delete(t){const n=await this.openDbPromise;return new Promise((r,a)=>{const i=n.transaction([A],"readwrite").objectStore(A),c=this.createCompositeKey(t);try{const o=i.delete(c);o.onerror=l=>{a(B(l,"storage-delete"))},o.onsuccess=()=>{r()}}catch(o){a(p.create("storage-delete",{originalErrorMessage:o==null?void 0:o.message}))}})}createCompositeKey(t){return[this.appId,this.appName,this.namespace,t].join()}}/**
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
 */class ha{constructor(t){this.storage=t}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}async loadFromStorage(){const t=this.storage.getLastFetchStatus(),n=this.storage.getLastSuccessfulFetchTimestampMillis(),r=this.storage.getActiveConfig(),a=await t;a&&(this.lastFetchStatus=a);const s=await n;s&&(this.lastSuccessfulFetchTimestampMillis=s);const i=await r;i&&(this.activeConfig=i)}setLastFetchStatus(t){return this.lastFetchStatus=t,this.storage.setLastFetchStatus(t)}setLastSuccessfulFetchTimestampMillis(t){return this.lastSuccessfulFetchTimestampMillis=t,this.storage.setLastSuccessfulFetchTimestampMillis(t)}setActiveConfig(t){return this.activeConfig=t,this.storage.setActiveConfig(t)}}/**
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
 */function da(){T(new S(Yr,e,"PUBLIC").setMultipleInstances(!0)),I(z,Oe),I(z,Oe,"esm2017");function e(t,{instanceIdentifier:n}){const r=t.getProvider("app").getImmediate(),a=t.getProvider("installations-internal").getImmediate();if(typeof window>"u")throw p.create("registration-window");if(!ee())throw p.create("indexed-db-unavailable");const{projectId:s,apiKey:i,appId:c}=r.options;if(!s)throw p.create("registration-project-id");if(!i)throw p.create("registration-api-key");if(!c)throw p.create("registration-app-id");n=n||"firebase";const o=new ua(c,r.name,n),l=new ha(o),h=new te(z);h.logLevel=u.ERROR;const d=new ea(a,wn,n,s,i,c),f=new ra(d,o),g=new Qr(f,o,l,h),E=new ia(r,g,l,o,h);return Xr(E),E}}da();const fa=e=>Object.fromEntries(new URLSearchParams(e)),ga=()=>{const e=ft(),t=fa(e.search);return"utm_campaign"in t&&"utm_medium"in t&&"utm_source"in t?{traffic_campaign:t.utm_campaign,traffic_medium:t.utm_medium,traffic_source:t.utm_source}:{}},pa=()=>{const e=ga();return{logEvent:dt.useCallback((n,r)=>{},[e])}};var ht=(e=>(e.CLICKED_BOOKING="hasClickedBooking",e.CLICKED_CANCELED_SELECTED_OFFERS="hasClickedCancelOffers",e.CLICKED_DISABLED_SELECTED_OFFERS="hasClickedDisabledOffers",e.CLICKED_CONSULT_CGU="hasClickedConsultCGU",e.CLICKED_CONSULT_SUPPORT="hasClickedConsultSupport",e.CLICKED_CREATE_ACCOUNT="hasClickedCreateAccount",e.CLICKED_CREATE_VENUE="hasClickedCreateVenue",e.CLICKED_ADD_BANK_INFORMATIONS="hasClickedAddBankInformation",e.CLICKED_NO_PRICING_POINT_SELECTED_YET="hasClickedNoPricingPointSelectedYet",e.CLICKED_ADD_VENUE_IN_OFFERER="hasClickedAddVenueInOfferer",e.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL="hasClickedSeeLaterFromSuccessVenueCreationModal",e.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL="hasClickedSeeLaterFromSuccessOfferCreationModal",e.CLICKED_SAVE_VENUE="hasClickedSaveVenue",e.CLICKED_DOWNLOAD_BOOKINGS="hasClickedDownloadBooking",e.CLICKED_DOWNLOAD_BOOKINGS_CSV="hasClickedDownloadBookingCsv",e.CLICKED_DOWNLOAD_BOOKINGS_OTHER_FORMAT="hasClickedDownloadBookingOtherFormat",e.CLICKED_DOWNLOAD_BOOKINGS_XLS="hasClickedDownloadBookingXls",e.CLICKED_EDIT_PROFILE="hasClickedEditProfile",e.CLICKED_HOME_STATS_PENDING_OFFERS_FAQ="hasClickedHomeStatsPendingOffersFaq",e.CLICKED_FORGOTTEN_PASSWORD="hasClickedForgottenPassword",e.CLICKED_HELP_CENTER="hasClickedHelpCenter",e.CLICKED_HOME="hasClickedHome",e.CLICKED_LOGOUT="hasClickedLogout",e.CLICKED_OFFER="hasClickedOffer",e.CLICKED_OFFER_FORM_NAVIGATION="hasClickedOfferFormNavigation",e.CLICKED_ONBOARDING_FORM_NAVIGATION="HasClickedOnboardingFormNavigation",e.CLICKED_CANCEL_OFFER_CREATION="hasClickedCancelOfferCreation",e.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK="hasClickedPartnerBlockPreviewVenueLink",e.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK="hasClickedPartnerBlockCopyVenueLink",e.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK="hasClickedPartnerBlockDmsApplicationLink",e.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK="hasClickedPartnerBlockCollectiveHelpLink",e.CLICKED_PERSONAL_DATA="hasClickedConsultPersonalData",e.CLICKED_PRO="hasClickedPro",e.CLICKED_REIMBURSEMENT="hasClickedReimbursement",e.CLICKED_SHOW_BOOKINGS="hasClickedShowBooking",e.CLICKED_STATS="hasClickedOffererStats",e.CLICKED_TICKET="hasClickedTicket",e.CLICKED_TOGGLE_HIDE_OFFERER_NAME="hasClickedToggleHideOffererName",e.CLICKED_DUPLICATE_TEMPLATE_OFFER="hasClickedDuplicateTemplateOffer",e.CLICKED_BEST_PRACTICES_STUDIES="hasClickedBestPracticesAndStudies",e.CLICKED_HELP_LINK="hasClickedHelpLink",e.CLICKED_RESET_FILTERS="hasClickedResetFilter",e.CLICKED_SHOW_STATUS_FILTER="hasClickedShowStatusFilter",e.CLICKED_OMNI_SEARCH_CRITERIA="hasClickedOmniSearchCriteria",e.CLICKED_PAGINATION_NEXT_PAGE="hasClickedPaginationNextPage",e.CLICKED_PAGINATION_PREVIOUS_PAGE="hasClickedPaginationPreviousPage",e.CLICKED_CONTACT_OUR_TEAMS="hasClickedContactOurTeams",e.FIRST_LOGIN="firstLogin",e.PAGE_VIEW="page_view",e.SIGNUP_FORM_ABORT="signupFormAbort",e.SIGNUP_FORM_SUCCESS="signupFormSuccess",e.TUTO_PAGE_VIEW="tutoPageView",e.DELETE_DRAFT_OFFER="DeleteDraftOffer",e.CLICKED_NO_VENUE="hasClickedNoVenue",e.CLICKED_EAC_DMS_TIMELINE="hasClickedEacDmsTimeline",e.CLICKED_EAC_DMS_LINK="hasClickedEacDmsLink",e.CLICKED_CREATE_OFFER_FROM_REQUEST="hasClickedCreateOfferFromRequest",e.CLICKED_ADD_IMAGE="hasClickedAddImage",e.CLICKED_DELETE_STOCK="hasClickedDeleteStock",e.CLICKED_BULK_DELETE_STOCK="hasClickedBulkDeleteStock",e.CLICKED_DOWNLOAD_OFFER_BOOKINGS="hasDownloadedBookings",e.CLICKED_PAGE_FOR_APP_HOME="hasClickedPageForAppHome",e.CLICKED_PAGE_FOR_ADAGE_HOME="hasClickedPageForAdageHome",e.CLICKED_INVOICES_DOWNLOAD="hasClickedInvoicesDownload",e.CLICKED_PUBLISH_FUTURE_OFFER_EARLIER="hasClickedPublishFutureOfferEarlier",e))(ht||{});const Le={"help-link":"_help-link_1c4y5_2","help-link-text":"_help-link-text_1c4y5_10"},ma=()=>{const{logEvent:e}=pa();return P.jsxs("a",{onClick:()=>e(ht.CLICKED_HELP_LINK,{from:location.pathname}),className:Le["help-link"],href:"https://aide.passculture.app/hc/fr/articles/4411991940369--Acteurs-culturels-Comment-poster-une-offre-%C3%A0-destination-d-un-groupe-scolaire-",rel:"noreferrer",target:"_blank",children:[P.jsx(pt,{src:gt,alt:"",width:"42"}),P.jsx("span",{className:Le["help-link-text"],children:"Aide"})]})},Ta={title:"components/HelpLink",component:ma,decorators:[e=>P.jsx("div",{style:{width:500,height:500},children:P.jsx(e,{})})]},v={};var Re,ke,Pe;v.parameters={...v.parameters,docs:{...(Re=v.parameters)==null?void 0:Re.docs,source:{originalSource:"{}",...(Pe=(ke=v.parameters)==null?void 0:ke.docs)==null?void 0:Pe.source}}};const ya=["Default"];export{v as Default,ya as __namedExportsOrder,Ta as default};
