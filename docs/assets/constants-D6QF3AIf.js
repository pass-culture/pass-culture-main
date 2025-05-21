import{r as Wt}from"./index-ClcD9ViR.js";import"./config-BqmKEuqZ.js";import{u as zt}from"./chunk-D4RADZKF-nWvgSiz2.js";/**
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
 */const qe=function(e){const t=[];let n=0;for(let r=0;r<e.length;r++){let a=e.charCodeAt(r);a<128?t[n++]=a:a<2048?(t[n++]=a>>6|192,t[n++]=a&63|128):(a&64512)===55296&&r+1<e.length&&(e.charCodeAt(r+1)&64512)===56320?(a=65536+((a&1023)<<10)+(e.charCodeAt(++r)&1023),t[n++]=a>>18|240,t[n++]=a>>12&63|128,t[n++]=a>>6&63|128,t[n++]=a&63|128):(t[n++]=a>>12|224,t[n++]=a>>6&63|128,t[n++]=a&63|128)}return t},Yt=function(e){const t=[];let n=0,r=0;for(;n<e.length;){const a=e[n++];if(a<128)t[r++]=String.fromCharCode(a);else if(a>191&&a<224){const s=e[n++];t[r++]=String.fromCharCode((a&31)<<6|s&63)}else if(a>239&&a<365){const s=e[n++],i=e[n++],o=e[n++],c=((a&7)<<18|(s&63)<<12|(i&63)<<6|o&63)-65536;t[r++]=String.fromCharCode(55296+(c>>10)),t[r++]=String.fromCharCode(56320+(c&1023))}else{const s=e[n++],i=e[n++];t[r++]=String.fromCharCode((a&15)<<12|(s&63)<<6|i&63)}}return t.join("")},Jt={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(e,t){if(!Array.isArray(e))throw Error("encodeByteArray takes an array as a parameter");this.init_();const n=t?this.byteToCharMapWebSafe_:this.byteToCharMap_,r=[];for(let a=0;a<e.length;a+=3){const s=e[a],i=a+1<e.length,o=i?e[a+1]:0,c=a+2<e.length,l=c?e[a+2]:0,h=s>>2,d=(s&3)<<4|o>>4;let f=(o&15)<<2|l>>6,g=l&63;c||(g=64,i||(f=64)),r.push(n[h],n[d],n[f],n[g])}return r.join("")},encodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?btoa(e):this.encodeByteArray(qe(e),t)},decodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?atob(e):Yt(this.decodeStringToByteArray(e,t))},decodeStringToByteArray(e,t){this.init_();const n=t?this.charToByteMapWebSafe_:this.charToByteMap_,r=[];for(let a=0;a<e.length;){const s=n[e.charAt(a++)],o=a<e.length?n[e.charAt(a)]:0;++a;const l=a<e.length?n[e.charAt(a)]:64;++a;const d=a<e.length?n[e.charAt(a)]:64;if(++a,s==null||o==null||l==null||d==null)throw new Xt;const f=s<<2|o>>4;if(r.push(f),l!==64){const g=o<<4&240|l>>2;if(r.push(g),d!==64){const A=l<<6&192|d;r.push(A)}}}return r},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let e=0;e<this.ENCODED_VALS.length;e++)this.byteToCharMap_[e]=this.ENCODED_VALS.charAt(e),this.charToByteMap_[this.byteToCharMap_[e]]=e,this.byteToCharMapWebSafe_[e]=this.ENCODED_VALS_WEBSAFE.charAt(e),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[e]]=e,e>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(e)]=e,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(e)]=e)}}};class Xt extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const Qt=function(e){const t=qe(e);return Jt.encodeByteArray(t,!0)},We=function(e){return Qt(e).replace(/\./g,"")};function Zt(){const e=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof e=="object"&&e.id!==void 0}function ze(){try{return typeof indexedDB=="object"}catch{return!1}}function Ye(){return new Promise((e,t)=>{try{let n=!0;const r="validate-browser-context-for-indexeddb-analytics-module",a=self.indexedDB.open(r);a.onsuccess=()=>{a.result.close(),n||self.indexedDB.deleteDatabase(r),e(!0)},a.onupgradeneeded=()=>{n=!1},a.onerror=()=>{var s;t(((s=a.error)===null||s===void 0?void 0:s.message)||"")}}catch(n){t(n)}})}function en(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
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
 */const tn="FirebaseError";let N=class Je extends Error{constructor(t,n,r){super(n),this.code=t,this.customData=r,this.name=tn,Object.setPrototypeOf(this,Je.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,V.prototype.create)}},V=class{constructor(t,n,r){this.service=t,this.serviceName=n,this.errors=r}create(t,...n){const r=n[0]||{},a=`${this.service}/${t}`,s=this.errors[t],i=s?nn(s,r):"Error",o=`${this.serviceName}: ${i} (${a}).`;return new N(a,o,r)}};function nn(e,t){return e.replace(rn,(n,r)=>{const a=t[r];return a!=null?String(a):`<${r}?>`})}const rn=/\{\$([^}]+)}/g;/**
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
 */const an=1e3,sn=2,on=4*60*60*1e3,cn=.5;function we(e,t=an,n=sn){const r=t*Math.pow(n,e),a=Math.round(cn*r*(Math.random()-.5)*2);return Math.min(on,r+a)}/**
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
 */function ln(e){return e&&e._delegate?e._delegate:e}let R=class{constructor(t,n,r){this.name=t,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}};/**
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
 */var u;(function(e){e[e.DEBUG=0]="DEBUG",e[e.VERBOSE=1]="VERBOSE",e[e.INFO=2]="INFO",e[e.WARN=3]="WARN",e[e.ERROR=4]="ERROR",e[e.SILENT=5]="SILENT"})(u||(u={}));const un={debug:u.DEBUG,verbose:u.VERBOSE,info:u.INFO,warn:u.WARN,error:u.ERROR,silent:u.SILENT},dn=u.INFO,hn={[u.DEBUG]:"log",[u.VERBOSE]:"log",[u.INFO]:"info",[u.WARN]:"warn",[u.ERROR]:"error"},fn=(e,t,...n)=>{if(t<e.logLevel)return;const r=new Date().toISOString(),a=hn[t];if(a)console[a](`[${r}]  ${e.name}:`,...n);else throw new Error(`Attempted to log a message with an invalid logType (value: ${t})`)};class ce{constructor(t){this.name=t,this._logLevel=dn,this._logHandler=fn,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(t){if(!(t in u))throw new TypeError(`Invalid value "${t}" assigned to \`logLevel\``);this._logLevel=t}setLogLevel(t){this._logLevel=typeof t=="string"?un[t]:t}get logHandler(){return this._logHandler}set logHandler(t){if(typeof t!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=t}get userLogHandler(){return this._userLogHandler}set userLogHandler(t){this._userLogHandler=t}debug(...t){this._userLogHandler&&this._userLogHandler(this,u.DEBUG,...t),this._logHandler(this,u.DEBUG,...t)}log(...t){this._userLogHandler&&this._userLogHandler(this,u.VERBOSE,...t),this._logHandler(this,u.VERBOSE,...t)}info(...t){this._userLogHandler&&this._userLogHandler(this,u.INFO,...t),this._logHandler(this,u.INFO,...t)}warn(...t){this._userLogHandler&&this._userLogHandler(this,u.WARN,...t),this._logHandler(this,u.WARN,...t)}error(...t){this._userLogHandler&&this._userLogHandler(this,u.ERROR,...t),this._logHandler(this,u.ERROR,...t)}}const gn=(e,t)=>t.some(n=>e instanceof n);let Te,Se;function pn(){return Te||(Te=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function mn(){return Se||(Se=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const Xe=new WeakMap,re=new WeakMap,Qe=new WeakMap,W=new WeakMap,le=new WeakMap;function Cn(e){const t=new Promise((n,r)=>{const a=()=>{e.removeEventListener("success",s),e.removeEventListener("error",i)},s=()=>{n(y(e.result)),a()},i=()=>{r(e.error),a()};e.addEventListener("success",s),e.addEventListener("error",i)});return t.then(n=>{n instanceof IDBCursor&&Xe.set(n,e)}).catch(()=>{}),le.set(t,e),t}function _n(e){if(re.has(e))return;const t=new Promise((n,r)=>{const a=()=>{e.removeEventListener("complete",s),e.removeEventListener("error",i),e.removeEventListener("abort",i)},s=()=>{n(),a()},i=()=>{r(e.error||new DOMException("AbortError","AbortError")),a()};e.addEventListener("complete",s),e.addEventListener("error",i),e.addEventListener("abort",i)});re.set(e,t)}let ae={get(e,t,n){if(e instanceof IDBTransaction){if(t==="done")return re.get(e);if(t==="objectStoreNames")return e.objectStoreNames||Qe.get(e);if(t==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return y(e[t])},set(e,t,n){return e[t]=n,!0},has(e,t){return e instanceof IDBTransaction&&(t==="done"||t==="store")?!0:t in e}};function In(e){ae=e(ae)}function En(e){return e===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(t,...n){const r=e.call(z(this),t,...n);return Qe.set(r,t.sort?t.sort():[t]),y(r)}:mn().includes(e)?function(...t){return e.apply(z(this),t),y(Xe.get(this))}:function(...t){return y(e.apply(z(this),t))}}function bn(e){return typeof e=="function"?En(e):(e instanceof IDBTransaction&&_n(e),gn(e,pn())?new Proxy(e,ae):e)}function y(e){if(e instanceof IDBRequest)return Cn(e);if(W.has(e))return W.get(e);const t=bn(e);return t!==e&&(W.set(e,t),le.set(t,e)),t}const z=e=>le.get(e);function ue(e,t,{blocked:n,upgrade:r,blocking:a,terminated:s}={}){const i=indexedDB.open(e,t),o=y(i);return r&&i.addEventListener("upgradeneeded",c=>{r(y(i.result),c.oldVersion,c.newVersion,y(i.transaction),c)}),n&&i.addEventListener("blocked",c=>n(c.oldVersion,c.newVersion,c)),o.then(c=>{s&&c.addEventListener("close",()=>s()),a&&c.addEventListener("versionchange",l=>a(l.oldVersion,l.newVersion,l))}).catch(()=>{}),o}const wn=["get","getKey","getAll","getAllKeys","count"],Tn=["put","add","delete","clear"],Y=new Map;function ye(e,t){if(!(e instanceof IDBDatabase&&!(t in e)&&typeof t=="string"))return;if(Y.get(t))return Y.get(t);const n=t.replace(/FromIndex$/,""),r=t!==n,a=Tn.includes(n);if(!(n in(r?IDBIndex:IDBObjectStore).prototype)||!(a||wn.includes(n)))return;const s=async function(i,...o){const c=this.transaction(i,a?"readwrite":"readonly");let l=c.store;return r&&(l=l.index(o.shift())),(await Promise.all([l[n](...o),a&&c.done]))[0]};return Y.set(t,s),s}In(e=>({...e,get:(t,n,r)=>ye(t,n)||e.get(t,n,r),has:(t,n)=>!!ye(t,n)||e.has(t,n)}));/**
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
 */class Sn{constructor(t){this.container=t}getPlatformInfoString(){return this.container.getProviders().map(n=>{if(yn(n)){const r=n.getImmediate();return`${r.library}/${r.version}`}else return null}).filter(n=>n).join(" ")}}function yn(e){const t=e.getComponent();return(t==null?void 0:t.type)==="VERSION"}const se="@firebase/app",Ae="0.13.0";/**
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
 */const b=new ce("@firebase/app"),An="@firebase/app-compat",Dn="@firebase/analytics-compat",On="@firebase/analytics",Rn="@firebase/app-check-compat",Ln="@firebase/app-check",kn="@firebase/auth",$n="@firebase/auth-compat",Pn="@firebase/database",Fn="@firebase/data-connect",Mn="@firebase/database-compat",Nn="@firebase/functions",vn="@firebase/functions-compat",Bn="@firebase/installations",Kn="@firebase/installations-compat",Vn="@firebase/messaging",Hn="@firebase/messaging-compat",xn="@firebase/performance",Un="@firebase/performance-compat",jn="@firebase/remote-config",Gn="@firebase/remote-config-compat",qn="@firebase/storage",Wn="@firebase/storage-compat",zn="@firebase/firestore",Yn="@firebase/ai",Jn="@firebase/firestore-compat",Xn="firebase",Qn="11.8.0",Zn={[se]:"fire-core",[An]:"fire-core-compat",[On]:"fire-analytics",[Dn]:"fire-analytics-compat",[Ln]:"fire-app-check",[Rn]:"fire-app-check-compat",[kn]:"fire-auth",[$n]:"fire-auth-compat",[Pn]:"fire-rtdb",[Fn]:"fire-data-connect",[Mn]:"fire-rtdb-compat",[Nn]:"fire-fn",[vn]:"fire-fn-compat",[Bn]:"fire-iid",[Kn]:"fire-iid-compat",[Vn]:"fire-fcm",[Hn]:"fire-fcm-compat",[xn]:"fire-perf",[Un]:"fire-perf-compat",[jn]:"fire-rc",[Gn]:"fire-rc-compat",[qn]:"fire-gcs",[Wn]:"fire-gcs-compat",[zn]:"fire-fst",[Jn]:"fire-fst-compat",[Yn]:"fire-vertex","fire-js":"fire-js",[Xn]:"fire-js-all"};/**
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
 */const er=new Map,tr=new Map,De=new Map;function Oe(e,t){try{e.container.addComponent(t)}catch(n){b.debug(`Component ${t.name} failed to register with FirebaseApp ${e.name}`,n)}}function E(e){const t=e.name;if(De.has(t))return b.debug(`There were multiple attempts to register component ${t}.`),!1;De.set(t,e);for(const n of er.values())Oe(n,e);for(const n of tr.values())Oe(n,e);return!0}function H(e,t){const n=e.container.getProvider("heartbeat").getImmediate({optional:!0});return n&&n.triggerHeartbeat(),e.container.getProvider(t)}/**
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
 */const nr={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},de=new V("app","Firebase",nr);/**
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
 */const rr=Qn;function I(e,t,n){var r;let a=(r=Zn[e])!==null&&r!==void 0?r:e;n&&(a+=`-${n}`);const s=a.match(/\s|\//),i=t.match(/\s|\//);if(s||i){const o=[`Unable to register library "${a}" with version "${t}":`];s&&o.push(`library name "${a}" contains illegal characters (whitespace or "/")`),s&&i&&o.push("and"),i&&o.push(`version name "${t}" contains illegal characters (whitespace or "/")`),b.warn(o.join(" "));return}E(new R(`${a}-version`,()=>({library:a,version:t}),"VERSION"))}/**
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
 */const ar="firebase-heartbeat-database",sr=1,M="firebase-heartbeat-store";let J=null;function Ze(){return J||(J=ue(ar,sr,{upgrade:(e,t)=>{switch(t){case 0:try{e.createObjectStore(M)}catch(n){console.warn(n)}}}}).catch(e=>{throw de.create("idb-open",{originalErrorMessage:e.message})})),J}async function ir(e){try{const n=(await Ze()).transaction(M),r=await n.objectStore(M).get(et(e));return await n.done,r}catch(t){if(t instanceof N)b.warn(t.message);else{const n=de.create("idb-get",{originalErrorMessage:t==null?void 0:t.message});b.warn(n.message)}}}async function Re(e,t){try{const r=(await Ze()).transaction(M,"readwrite");await r.objectStore(M).put(t,et(e)),await r.done}catch(n){if(n instanceof N)b.warn(n.message);else{const r=de.create("idb-set",{originalErrorMessage:n==null?void 0:n.message});b.warn(r.message)}}}function et(e){return`${e.name}!${e.options.appId}`}/**
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
 */const or=1024,cr=30;class lr{constructor(t){this.container=t,this._heartbeatsCache=null;const n=this.container.getProvider("app").getImmediate();this._storage=new dr(n),this._heartbeatsCachePromise=this._storage.read().then(r=>(this._heartbeatsCache=r,r))}async triggerHeartbeat(){var t,n;try{const a=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),s=Le();if(((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,((n=this._heartbeatsCache)===null||n===void 0?void 0:n.heartbeats)==null)||this._heartbeatsCache.lastSentHeartbeatDate===s||this._heartbeatsCache.heartbeats.some(i=>i.date===s))return;if(this._heartbeatsCache.heartbeats.push({date:s,agent:a}),this._heartbeatsCache.heartbeats.length>cr){const i=hr(this._heartbeatsCache.heartbeats);this._heartbeatsCache.heartbeats.splice(i,1)}return this._storage.overwrite(this._heartbeatsCache)}catch(r){b.warn(r)}}async getHeartbeatsHeader(){var t;try{if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null||this._heartbeatsCache.heartbeats.length===0)return"";const n=Le(),{heartbeatsToSend:r,unsentEntries:a}=ur(this._heartbeatsCache.heartbeats),s=We(JSON.stringify({version:2,heartbeats:r}));return this._heartbeatsCache.lastSentHeartbeatDate=n,a.length>0?(this._heartbeatsCache.heartbeats=a,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),s}catch(n){return b.warn(n),""}}}function Le(){return new Date().toISOString().substring(0,10)}function ur(e,t=or){const n=[];let r=e.slice();for(const a of e){const s=n.find(i=>i.agent===a.agent);if(s){if(s.dates.push(a.date),ke(n)>t){s.dates.pop();break}}else if(n.push({agent:a.agent,dates:[a.date]}),ke(n)>t){n.pop();break}r=r.slice(1)}return{heartbeatsToSend:n,unsentEntries:r}}class dr{constructor(t){this.app=t,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return ze()?Ye().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const n=await ir(this.app);return n!=null&&n.heartbeats?n:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(t){var n;if(await this._canUseIndexedDBPromise){const a=await this.read();return Re(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:a.lastSentHeartbeatDate,heartbeats:t.heartbeats})}else return}async add(t){var n;if(await this._canUseIndexedDBPromise){const a=await this.read();return Re(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:a.lastSentHeartbeatDate,heartbeats:[...a.heartbeats,...t.heartbeats]})}else return}}function ke(e){return We(JSON.stringify({version:2,heartbeats:e})).length}function hr(e){if(e.length===0)return-1;let t=0,n=e[0].date;for(let r=1;r<e.length;r++)e[r].date<n&&(n=e[r].date,t=r);return t}/**
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
 */function fr(e){E(new R("platform-logger",t=>new Sn(t),"PRIVATE")),E(new R("heartbeat",t=>new lr(t),"PRIVATE")),I(se,Ae,e),I(se,Ae,"esm2017"),I("fire-js","")}fr("");const tt="@firebase/installations",he="0.6.17";/**
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
 */const nt=1e4,rt=`w:${he}`,at="FIS_v2",gr="https://firebaseinstallations.googleapis.com/v1",pr=60*60*1e3,mr="installations",Cr="Installations";/**
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
 */const _r={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},L=new V(mr,Cr,_r);function st(e){return e instanceof N&&e.code.includes("request-failed")}/**
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
 */function it({projectId:e}){return`${gr}/projects/${e}/installations`}function ot(e){return{token:e.token,requestStatus:2,expiresIn:Er(e.expiresIn),creationTime:Date.now()}}async function ct(e,t){const r=(await t.json()).error;return L.create("request-failed",{requestName:e,serverCode:r.code,serverMessage:r.message,serverStatus:r.status})}function lt({apiKey:e}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e})}function Ir(e,{refreshToken:t}){const n=lt(e);return n.append("Authorization",br(t)),n}async function ut(e){const t=await e();return t.status>=500&&t.status<600?e():t}function Er(e){return Number(e.replace("s","000"))}function br(e){return`${at} ${e}`}/**
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
 */async function wr({appConfig:e,heartbeatServiceProvider:t},{fid:n}){const r=it(e),a=lt(e),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&a.append("x-firebase-client",l)}const i={fid:n,authVersion:at,appId:e.appId,sdkVersion:rt},o={method:"POST",headers:a,body:JSON.stringify(i)},c=await ut(()=>fetch(r,o));if(c.ok){const l=await c.json();return{fid:l.fid||n,registrationStatus:2,refreshToken:l.refreshToken,authToken:ot(l.authToken)}}else throw await ct("Create Installation",c)}/**
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
 */function dt(e){return new Promise(t=>{setTimeout(t,e)})}/**
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
 */function Tr(e){return btoa(String.fromCharCode(...e)).replace(/\+/g,"-").replace(/\//g,"_")}/**
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
 */const Sr=/^[cdef][\w-]{21}$/,ie="";function yr(){try{const e=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(e),e[0]=112+e[0]%16;const n=Ar(e);return Sr.test(n)?n:ie}catch{return ie}}function Ar(e){return Tr(e).substr(0,22)}/**
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
 */const ht=new Map;function ft(e,t){const n=x(e);gt(n,t),Dr(n,t)}function gt(e,t){const n=ht.get(e);if(n)for(const r of n)r(t)}function Dr(e,t){const n=Or();n&&n.postMessage({key:e,fid:t}),Rr()}let D=null;function Or(){return!D&&"BroadcastChannel"in self&&(D=new BroadcastChannel("[Firebase] FID Change"),D.onmessage=e=>{gt(e.data.key,e.data.fid)}),D}function Rr(){ht.size===0&&D&&(D.close(),D=null)}/**
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
 */const Lr="firebase-installations-database",kr=1,k="firebase-installations-store";let X=null;function fe(){return X||(X=ue(Lr,kr,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(k)}}})),X}async function B(e,t){const n=x(e),a=(await fe()).transaction(k,"readwrite"),s=a.objectStore(k),i=await s.get(n);return await s.put(t,n),await a.done,(!i||i.fid!==t.fid)&&ft(e,t.fid),t}async function pt(e){const t=x(e),r=(await fe()).transaction(k,"readwrite");await r.objectStore(k).delete(t),await r.done}async function U(e,t){const n=x(e),a=(await fe()).transaction(k,"readwrite"),s=a.objectStore(k),i=await s.get(n),o=t(i);return o===void 0?await s.delete(n):await s.put(o,n),await a.done,o&&(!i||i.fid!==o.fid)&&ft(e,o.fid),o}/**
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
 */async function ge(e){let t;const n=await U(e.appConfig,r=>{const a=$r(r),s=Pr(e,a);return t=s.registrationPromise,s.installationEntry});return n.fid===ie?{installationEntry:await t}:{installationEntry:n,registrationPromise:t}}function $r(e){const t=e||{fid:yr(),registrationStatus:0};return mt(t)}function Pr(e,t){if(t.registrationStatus===0){if(!navigator.onLine){const a=Promise.reject(L.create("app-offline"));return{installationEntry:t,registrationPromise:a}}const n={fid:t.fid,registrationStatus:1,registrationTime:Date.now()},r=Fr(e,n);return{installationEntry:n,registrationPromise:r}}else return t.registrationStatus===1?{installationEntry:t,registrationPromise:Mr(e)}:{installationEntry:t}}async function Fr(e,t){try{const n=await wr(e,t);return B(e.appConfig,n)}catch(n){throw st(n)&&n.customData.serverCode===409?await pt(e.appConfig):await B(e.appConfig,{fid:t.fid,registrationStatus:0}),n}}async function Mr(e){let t=await $e(e.appConfig);for(;t.registrationStatus===1;)await dt(100),t=await $e(e.appConfig);if(t.registrationStatus===0){const{installationEntry:n,registrationPromise:r}=await ge(e);return r||n}return t}function $e(e){return U(e,t=>{if(!t)throw L.create("installation-not-found");return mt(t)})}function mt(e){return Nr(e)?{fid:e.fid,registrationStatus:0}:e}function Nr(e){return e.registrationStatus===1&&e.registrationTime+nt<Date.now()}/**
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
 */async function vr({appConfig:e,heartbeatServiceProvider:t},n){const r=Br(e,n),a=Ir(e,n),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&a.append("x-firebase-client",l)}const i={installation:{sdkVersion:rt,appId:e.appId}},o={method:"POST",headers:a,body:JSON.stringify(i)},c=await ut(()=>fetch(r,o));if(c.ok){const l=await c.json();return ot(l)}else throw await ct("Generate Auth Token",c)}function Br(e,{fid:t}){return`${it(e)}/${t}/authTokens:generate`}/**
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
 */async function pe(e,t=!1){let n;const r=await U(e.appConfig,s=>{if(!Ct(s))throw L.create("not-registered");const i=s.authToken;if(!t&&Hr(i))return s;if(i.requestStatus===1)return n=Kr(e,t),s;{if(!navigator.onLine)throw L.create("app-offline");const o=Ur(s);return n=Vr(e,o),o}});return n?await n:r.authToken}async function Kr(e,t){let n=await Pe(e.appConfig);for(;n.authToken.requestStatus===1;)await dt(100),n=await Pe(e.appConfig);const r=n.authToken;return r.requestStatus===0?pe(e,t):r}function Pe(e){return U(e,t=>{if(!Ct(t))throw L.create("not-registered");const n=t.authToken;return jr(n)?Object.assign(Object.assign({},t),{authToken:{requestStatus:0}}):t})}async function Vr(e,t){try{const n=await vr(e,t),r=Object.assign(Object.assign({},t),{authToken:n});return await B(e.appConfig,r),n}catch(n){if(st(n)&&(n.customData.serverCode===401||n.customData.serverCode===404))await pt(e.appConfig);else{const r=Object.assign(Object.assign({},t),{authToken:{requestStatus:0}});await B(e.appConfig,r)}throw n}}function Ct(e){return e!==void 0&&e.registrationStatus===2}function Hr(e){return e.requestStatus===2&&!xr(e)}function xr(e){const t=Date.now();return t<e.creationTime||e.creationTime+e.expiresIn<t+pr}function Ur(e){const t={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},e),{authToken:t})}function jr(e){return e.requestStatus===1&&e.requestTime+nt<Date.now()}/**
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
 */async function Gr(e){const t=e,{installationEntry:n,registrationPromise:r}=await ge(t);return r?r.catch(console.error):pe(t).catch(console.error),n.fid}/**
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
 */async function qr(e,t=!1){const n=e;return await Wr(n),(await pe(n,t)).token}async function Wr(e){const{registrationPromise:t}=await ge(e);t&&await t}/**
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
 */function zr(e){if(!e||!e.options)throw Q("App Configuration");if(!e.name)throw Q("App Name");const t=["projectId","apiKey","appId"];for(const n of t)if(!e.options[n])throw Q(n);return{appName:e.name,projectId:e.options.projectId,apiKey:e.options.apiKey,appId:e.options.appId}}function Q(e){return L.create("missing-app-config-values",{valueName:e})}/**
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
 */const _t="installations",Yr="installations-internal",Jr=e=>{const t=e.getProvider("app").getImmediate(),n=zr(t),r=H(t,"heartbeat");return{app:t,appConfig:n,heartbeatServiceProvider:r,_delete:()=>Promise.resolve()}},Xr=e=>{const t=e.getProvider("app").getImmediate(),n=H(t,_t).getImmediate();return{getId:()=>Gr(n),getToken:a=>qr(n,a)}};function Qr(){E(new R(_t,Jr,"PUBLIC")),E(new R(Yr,Xr,"PRIVATE"))}Qr();I(tt,he);I(tt,he,"esm2017");/**
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
 */const Fe="analytics",Zr="firebase_id",ea="origin",ta=60*1e3,na="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",me="https://www.googletagmanager.com/gtag/js";/**
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
 */const p=new ce("@firebase/analytics");/**
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
 */const ra={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-initialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},C=new V("analytics","Analytics",ra);/**
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
 */function aa(e){if(!e.startsWith(me)){const t=C.create("invalid-gtag-resource",{gtagURL:e});return p.warn(t.message),""}return e}function It(e){return Promise.all(e.map(t=>t.catch(n=>n)))}function sa(e,t){let n;return window.trustedTypes&&(n=window.trustedTypes.createPolicy(e,t)),n}function ia(e,t){const n=sa("firebase-js-sdk-policy",{createScriptURL:aa}),r=document.createElement("script"),a=`${me}?l=${e}&id=${t}`;r.src=n?n==null?void 0:n.createScriptURL(a):a,r.async=!0,document.head.appendChild(r)}function oa(e){let t=[];return Array.isArray(window[e])?t=window[e]:window[e]=t,t}async function ca(e,t,n,r,a,s){const i=r[a];try{if(i)await t[i];else{const c=(await It(n)).find(l=>l.measurementId===a);c&&await t[c.appId]}}catch(o){p.error(o)}e("config",a,s)}async function la(e,t,n,r,a){try{let s=[];if(a&&a.send_to){let i=a.send_to;Array.isArray(i)||(i=[i]);const o=await It(n);for(const c of i){const l=o.find(d=>d.measurementId===c),h=l&&t[l.appId];if(h)s.push(h);else{s=[];break}}}s.length===0&&(s=Object.values(t)),await Promise.all(s),e("event",r,a||{})}catch(s){p.error(s)}}function ua(e,t,n,r){async function a(s,...i){try{if(s==="event"){const[o,c]=i;await la(e,t,n,o,c)}else if(s==="config"){const[o,c]=i;await ca(e,t,n,r,o,c)}else if(s==="consent"){const[o,c]=i;e("consent",o,c)}else if(s==="get"){const[o,c,l]=i;e("get",o,c,l)}else if(s==="set"){const[o]=i;e("set",o)}else e(s,...i)}catch(o){p.error(o)}}return a}function da(e,t,n,r,a){let s=function(...i){window[r].push(arguments)};return window[a]&&typeof window[a]=="function"&&(s=window[a]),window[a]=ua(s,e,t,n),{gtagCore:s,wrappedGtag:window[a]}}function ha(e){const t=window.document.getElementsByTagName("script");for(const n of Object.values(t))if(n.src&&n.src.includes(me)&&n.src.includes(e))return n;return null}/**
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
 */const fa=30,ga=1e3;class pa{constructor(t={},n=ga){this.throttleMetadata=t,this.intervalMillis=n}getThrottleMetadata(t){return this.throttleMetadata[t]}setThrottleMetadata(t,n){this.throttleMetadata[t]=n}deleteThrottleMetadata(t){delete this.throttleMetadata[t]}}const Et=new pa;function ma(e){return new Headers({Accept:"application/json","x-goog-api-key":e})}async function Ca(e){var t;const{appId:n,apiKey:r}=e,a={method:"GET",headers:ma(r)},s=na.replace("{app-id}",n),i=await fetch(s,a);if(i.status!==200&&i.status!==304){let o="";try{const c=await i.json();!((t=c.error)===null||t===void 0)&&t.message&&(o=c.error.message)}catch{}throw C.create("config-fetch-failed",{httpStatus:i.status,responseMessage:o})}return i.json()}async function _a(e,t=Et,n){const{appId:r,apiKey:a,measurementId:s}=e.options;if(!r)throw C.create("no-app-id");if(!a){if(s)return{measurementId:s,appId:r};throw C.create("no-api-key")}const i=t.getThrottleMetadata(r)||{backoffCount:0,throttleEndTimeMillis:Date.now()},o=new ba;return setTimeout(async()=>{o.abort()},ta),bt({appId:r,apiKey:a,measurementId:s},i,o,t)}async function bt(e,{throttleEndTimeMillis:t,backoffCount:n},r,a=Et){var s;const{appId:i,measurementId:o}=e;try{await Ia(r,t)}catch(c){if(o)return p.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${o} provided in the "measurementId" field in the local Firebase config. [${c==null?void 0:c.message}]`),{appId:i,measurementId:o};throw c}try{const c=await Ca(e);return a.deleteThrottleMetadata(i),c}catch(c){const l=c;if(!Ea(l)){if(a.deleteThrottleMetadata(i),o)return p.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${o} provided in the "measurementId" field in the local Firebase config. [${l==null?void 0:l.message}]`),{appId:i,measurementId:o};throw c}const h=Number((s=l==null?void 0:l.customData)===null||s===void 0?void 0:s.httpStatus)===503?we(n,a.intervalMillis,fa):we(n,a.intervalMillis),d={throttleEndTimeMillis:Date.now()+h,backoffCount:n+1};return a.setThrottleMetadata(i,d),p.debug(`Calling attemptFetch again in ${h} millis`),bt(e,d,r,a)}}function Ia(e,t){return new Promise((n,r)=>{const a=Math.max(t-Date.now(),0),s=setTimeout(n,a);e.addEventListener(()=>{clearTimeout(s),r(C.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function Ea(e){if(!(e instanceof N)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class ba{constructor(){this.listeners=[]}addEventListener(t){this.listeners.push(t)}abort(){this.listeners.forEach(t=>t())}}async function wa(e,t,n,r,a){if(a&&a.global){e("event",n,r);return}else{const s=await t,i=Object.assign(Object.assign({},r),{send_to:s});e("event",n,i)}}/**
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
 */async function Ta(){if(ze())try{await Ye()}catch(e){return p.warn(C.create("indexeddb-unavailable",{errorInfo:e==null?void 0:e.toString()}).message),!1}else return p.warn(C.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function Sa(e,t,n,r,a,s,i){var o;const c=_a(e);c.then(g=>{n[g.measurementId]=g.appId,e.options.measurementId&&g.measurementId!==e.options.measurementId&&p.warn(`The measurement ID in the local Firebase config (${e.options.measurementId}) does not match the measurement ID fetched from the server (${g.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(g=>p.error(g)),t.push(c);const l=Ta().then(g=>{if(g)return r.getId()}),[h,d]=await Promise.all([c,l]);ha(s)||ia(s,h.measurementId),a("js",new Date);const f=(o=i==null?void 0:i.config)!==null&&o!==void 0?o:{};return f[ea]="firebase",f.update=!0,d!=null&&(f[Zr]=d),a("config",h.measurementId,f),h.measurementId}/**
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
 */class ya{constructor(t){this.app=t}_delete(){return delete F[this.app.options.appId],Promise.resolve()}}let F={},Me=[];const Ne={};let Z="dataLayer",Aa="gtag",ve,wt,Be=!1;function Da(){const e=[];if(Zt()&&e.push("This is a browser extension environment."),en()||e.push("Cookies are not available."),e.length>0){const t=e.map((r,a)=>`(${a+1}) ${r}`).join(" "),n=C.create("invalid-analytics-context",{errorInfo:t});p.warn(n.message)}}function Oa(e,t,n){Da();const r=e.options.appId;if(!r)throw C.create("no-app-id");if(!e.options.apiKey)if(e.options.measurementId)p.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${e.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw C.create("no-api-key");if(F[r]!=null)throw C.create("already-exists",{id:r});if(!Be){oa(Z);const{wrappedGtag:s,gtagCore:i}=da(F,Me,Ne,Z,Aa);wt=s,ve=i,Be=!0}return F[r]=Sa(e,Me,Ne,t,ve,Z,n),new ya(e)}function Ra(e,t,n,r){e=ln(e),wa(wt,F[e.app.options.appId],t,n,r).catch(a=>p.error(a))}const Ke="@firebase/analytics",Ve="0.10.16";function La(){E(new R(Fe,(t,{options:n})=>{const r=t.getProvider("app").getImmediate(),a=t.getProvider("installations-internal").getImmediate();return Oa(r,a,n)},"PUBLIC")),E(new R("analytics-internal",e,"PRIVATE")),I(Ke,Ve),I(Ke,Ve,"esm2017");function e(t){try{const n=t.getProvider(Fe).getImmediate();return{logEvent:(r,a,s)=>Ra(n,r,a,s)}}catch(n){throw C.create("interop-component-reg-failed",{reason:n})}}}La();function ka(){try{return typeof indexedDB=="object"}catch{return!1}}/**
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
 */const $a="FirebaseError";let Tt=class St extends Error{constructor(t,n,r){super(n),this.code=t,this.customData=r,this.name=$a,Object.setPrototypeOf(this,St.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,yt.prototype.create)}},yt=class{constructor(t,n,r){this.service=t,this.serviceName=n,this.errors=r}create(t,...n){const r=n[0]||{},a=`${this.service}/${t}`,s=this.errors[t],i=s?Pa(s,r):"Error",o=`${this.serviceName}: ${i} (${a}).`;return new Tt(a,o,r)}};function Pa(e,t){return e.replace(Fa,(n,r)=>{const a=t[r];return a!=null?String(a):`<${r}?>`})}const Fa=/\{\$([^}]+)}/g;/**
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
 */const Ma=1e3,Na=2,va=4*60*60*1e3,Ba=.5;function Ka(e,t=Ma,n=Na){const r=t*Math.pow(n,e),a=Math.round(Ba*r*(Math.random()-.5)*2);return Math.min(va,r+a)}/**
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
 */function Va(e){return e&&e._delegate?e._delegate:e}let Ha=class{constructor(t,n,r){this.name=t,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}};/**
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
 */const xa="FirebaseError";class j extends Error{constructor(t,n,r){super(n),this.code=t,this.customData=r,this.name=xa,Object.setPrototypeOf(this,j.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,At.prototype.create)}}class At{constructor(t,n,r){this.service=t,this.serviceName=n,this.errors=r}create(t,...n){const r=n[0]||{},a=`${this.service}/${t}`,s=this.errors[t],i=s?Ua(s,r):"Error",o=`${this.serviceName}: ${i} (${a}).`;return new j(a,o,r)}}function Ua(e,t){return e.replace(ja,(n,r)=>{const a=t[r];return a!=null?String(a):`<${r}?>`})}const ja=/\{\$([^}]+)}/g;class He{constructor(t,n,r){this.name=t,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}}const Dt="@firebase/installations",Ce="0.6.16";/**
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
 */const Ot=1e4,Rt=`w:${Ce}`,Lt="FIS_v2",Ga="https://firebaseinstallations.googleapis.com/v1",qa=60*60*1e3,Wa="installations",za="Installations";/**
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
 */const Ya={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},$=new At(Wa,za,Ya);function kt(e){return e instanceof j&&e.code.includes("request-failed")}/**
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
 */function $t({projectId:e}){return`${Ga}/projects/${e}/installations`}function Pt(e){return{token:e.token,requestStatus:2,expiresIn:Xa(e.expiresIn),creationTime:Date.now()}}async function Ft(e,t){const r=(await t.json()).error;return $.create("request-failed",{requestName:e,serverCode:r.code,serverMessage:r.message,serverStatus:r.status})}function Mt({apiKey:e}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e})}function Ja(e,{refreshToken:t}){const n=Mt(e);return n.append("Authorization",Qa(t)),n}async function Nt(e){const t=await e();return t.status>=500&&t.status<600?e():t}function Xa(e){return Number(e.replace("s","000"))}function Qa(e){return`${Lt} ${e}`}/**
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
 */async function Za({appConfig:e,heartbeatServiceProvider:t},{fid:n}){const r=$t(e),a=Mt(e),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&a.append("x-firebase-client",l)}const i={fid:n,authVersion:Lt,appId:e.appId,sdkVersion:Rt},o={method:"POST",headers:a,body:JSON.stringify(i)},c=await Nt(()=>fetch(r,o));if(c.ok){const l=await c.json();return{fid:l.fid||n,registrationStatus:2,refreshToken:l.refreshToken,authToken:Pt(l.authToken)}}else throw await Ft("Create Installation",c)}/**
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
 */function vt(e){return new Promise(t=>{setTimeout(t,e)})}/**
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
 */function es(e){return btoa(String.fromCharCode(...e)).replace(/\+/g,"-").replace(/\//g,"_")}/**
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
 */const ts=/^[cdef][\w-]{21}$/,oe="";function ns(){try{const e=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(e),e[0]=112+e[0]%16;const n=rs(e);return ts.test(n)?n:oe}catch{return oe}}function rs(e){return es(e).substr(0,22)}/**
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
 */function G(e){return`${e.appName}!${e.appId}`}/**
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
 */const Bt=new Map;function Kt(e,t){const n=G(e);Vt(n,t),as(n,t)}function Vt(e,t){const n=Bt.get(e);if(n)for(const r of n)r(t)}function as(e,t){const n=ss();n&&n.postMessage({key:e,fid:t}),is()}let O=null;function ss(){return!O&&"BroadcastChannel"in self&&(O=new BroadcastChannel("[Firebase] FID Change"),O.onmessage=e=>{Vt(e.data.key,e.data.fid)}),O}function is(){Bt.size===0&&O&&(O.close(),O=null)}/**
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
 */const os="firebase-installations-database",cs=1,P="firebase-installations-store";let ee=null;function _e(){return ee||(ee=ue(os,cs,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(P)}}})),ee}async function K(e,t){const n=G(e),a=(await _e()).transaction(P,"readwrite"),s=a.objectStore(P),i=await s.get(n);return await s.put(t,n),await a.done,(!i||i.fid!==t.fid)&&Kt(e,t.fid),t}async function Ht(e){const t=G(e),r=(await _e()).transaction(P,"readwrite");await r.objectStore(P).delete(t),await r.done}async function q(e,t){const n=G(e),a=(await _e()).transaction(P,"readwrite"),s=a.objectStore(P),i=await s.get(n),o=t(i);return o===void 0?await s.delete(n):await s.put(o,n),await a.done,o&&(!i||i.fid!==o.fid)&&Kt(e,o.fid),o}/**
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
 */async function Ie(e){let t;const n=await q(e.appConfig,r=>{const a=ls(r),s=us(e,a);return t=s.registrationPromise,s.installationEntry});return n.fid===oe?{installationEntry:await t}:{installationEntry:n,registrationPromise:t}}function ls(e){const t=e||{fid:ns(),registrationStatus:0};return xt(t)}function us(e,t){if(t.registrationStatus===0){if(!navigator.onLine){const a=Promise.reject($.create("app-offline"));return{installationEntry:t,registrationPromise:a}}const n={fid:t.fid,registrationStatus:1,registrationTime:Date.now()},r=ds(e,n);return{installationEntry:n,registrationPromise:r}}else return t.registrationStatus===1?{installationEntry:t,registrationPromise:hs(e)}:{installationEntry:t}}async function ds(e,t){try{const n=await Za(e,t);return K(e.appConfig,n)}catch(n){throw kt(n)&&n.customData.serverCode===409?await Ht(e.appConfig):await K(e.appConfig,{fid:t.fid,registrationStatus:0}),n}}async function hs(e){let t=await xe(e.appConfig);for(;t.registrationStatus===1;)await vt(100),t=await xe(e.appConfig);if(t.registrationStatus===0){const{installationEntry:n,registrationPromise:r}=await Ie(e);return r||n}return t}function xe(e){return q(e,t=>{if(!t)throw $.create("installation-not-found");return xt(t)})}function xt(e){return fs(e)?{fid:e.fid,registrationStatus:0}:e}function fs(e){return e.registrationStatus===1&&e.registrationTime+Ot<Date.now()}/**
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
 */async function gs({appConfig:e,heartbeatServiceProvider:t},n){const r=ps(e,n),a=Ja(e,n),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&a.append("x-firebase-client",l)}const i={installation:{sdkVersion:Rt,appId:e.appId}},o={method:"POST",headers:a,body:JSON.stringify(i)},c=await Nt(()=>fetch(r,o));if(c.ok){const l=await c.json();return Pt(l)}else throw await Ft("Generate Auth Token",c)}function ps(e,{fid:t}){return`${$t(e)}/${t}/authTokens:generate`}/**
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
 */async function Ee(e,t=!1){let n;const r=await q(e.appConfig,s=>{if(!Ut(s))throw $.create("not-registered");const i=s.authToken;if(!t&&_s(i))return s;if(i.requestStatus===1)return n=ms(e,t),s;{if(!navigator.onLine)throw $.create("app-offline");const o=Es(s);return n=Cs(e,o),o}});return n?await n:r.authToken}async function ms(e,t){let n=await Ue(e.appConfig);for(;n.authToken.requestStatus===1;)await vt(100),n=await Ue(e.appConfig);const r=n.authToken;return r.requestStatus===0?Ee(e,t):r}function Ue(e){return q(e,t=>{if(!Ut(t))throw $.create("not-registered");const n=t.authToken;return bs(n)?Object.assign(Object.assign({},t),{authToken:{requestStatus:0}}):t})}async function Cs(e,t){try{const n=await gs(e,t),r=Object.assign(Object.assign({},t),{authToken:n});return await K(e.appConfig,r),n}catch(n){if(kt(n)&&(n.customData.serverCode===401||n.customData.serverCode===404))await Ht(e.appConfig);else{const r=Object.assign(Object.assign({},t),{authToken:{requestStatus:0}});await K(e.appConfig,r)}throw n}}function Ut(e){return e!==void 0&&e.registrationStatus===2}function _s(e){return e.requestStatus===2&&!Is(e)}function Is(e){const t=Date.now();return t<e.creationTime||e.creationTime+e.expiresIn<t+qa}function Es(e){const t={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},e),{authToken:t})}function bs(e){return e.requestStatus===1&&e.requestTime+Ot<Date.now()}/**
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
 */async function ws(e){const t=e,{installationEntry:n,registrationPromise:r}=await Ie(t);return r?r.catch(console.error):Ee(t).catch(console.error),n.fid}/**
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
 */async function Ts(e,t=!1){const n=e;return await Ss(n),(await Ee(n,t)).token}async function Ss(e){const{registrationPromise:t}=await Ie(e);t&&await t}/**
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
 */function ys(e){if(!e||!e.options)throw te("App Configuration");if(!e.name)throw te("App Name");const t=["projectId","apiKey","appId"];for(const n of t)if(!e.options[n])throw te(n);return{appName:e.name,projectId:e.options.projectId,apiKey:e.options.apiKey,appId:e.options.appId}}function te(e){return $.create("missing-app-config-values",{valueName:e})}/**
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
 */const jt="installations",As="installations-internal",Ds=e=>{const t=e.getProvider("app").getImmediate(),n=ys(t),r=H(t,"heartbeat");return{app:t,appConfig:n,heartbeatServiceProvider:r,_delete:()=>Promise.resolve()}},Os=e=>{const t=e.getProvider("app").getImmediate(),n=H(t,jt).getImmediate();return{getId:()=>ws(n),getToken:a=>Ts(n,a)}};function Rs(){E(new He(jt,Ds,"PUBLIC")),E(new He(As,Os,"PRIVATE"))}Rs();I(Dt,Ce);I(Dt,Ce,"esm2017");const ne="@firebase/remote-config",je="0.6.3";/**
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
 */const Ls="remote-config",Ge=100;/**
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
 */const ks={"already-initialized":"Remote Config already initialized","registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser","custom-signal-max-allowed-signals":"Setting more than {$maxSignals} custom signals is not supported."},m=new yt("remoteconfig","Remote Config",ks);function $s(e){const t=Va(e);return t._initializePromise||(t._initializePromise=t._storageCache.loadFromStorage().then(()=>{t._isInitializationComplete=!0})),t._initializePromise}/**
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
 */class Ps{constructor(t,n,r,a){this.client=t,this.storage=n,this.storageCache=r,this.logger=a}isCachedDataFresh(t,n){if(!n)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const r=Date.now()-n,a=r<=t;return this.logger.debug(`Config fetch cache check. Cache age millis: ${r}. Cache max age millis (minimumFetchIntervalMillis setting): ${t}. Is cache hit: ${a}.`),a}async fetch(t){const[n,r]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(r&&this.isCachedDataFresh(t.cacheMaxAgeMillis,n))return r;t.eTag=r&&r.eTag;const a=await this.client.fetch(t),s=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return a.status===200&&s.push(this.storage.setLastSuccessfulFetchResponse(a)),await Promise.all(s),a}}/**
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
 */function Fs(e=navigator){return e.languages&&e.languages[0]||e.language}/**
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
 */class Ms{constructor(t,n,r,a,s,i){this.firebaseInstallations=t,this.sdkVersion=n,this.namespace=r,this.projectId=a,this.apiKey=s,this.appId=i}async fetch(t){const[n,r]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),s=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,i={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":t.eTag||"*"},o={sdk_version:this.sdkVersion,app_instance_id:n,app_instance_id_token:r,app_id:this.appId,language_code:Fs(),custom_signals:t.customSignals},c={method:"POST",headers:i,body:JSON.stringify(o)},l=fetch(s,c),h=new Promise((_,T)=>{t.signal.addEventListener(()=>{const be=new Error("The operation was aborted.");be.name="AbortError",T(be)})});let d;try{await Promise.race([l,h]),d=await l}catch(_){let T="fetch-client-network";throw(_==null?void 0:_.name)==="AbortError"&&(T="fetch-timeout"),m.create(T,{originalErrorMessage:_==null?void 0:_.message})}let f=d.status;const g=d.headers.get("ETag")||void 0;let A,w;if(d.status===200){let _;try{_=await d.json()}catch(T){throw m.create("fetch-client-parse",{originalErrorMessage:T==null?void 0:T.message})}A=_.entries,w=_.state}if(w==="INSTANCE_STATE_UNSPECIFIED"?f=500:w==="NO_CHANGE"?f=304:(w==="NO_TEMPLATE"||w==="EMPTY_CONFIG")&&(A={}),f!==304&&f!==200)throw m.create("fetch-status",{httpStatus:f});return{status:f,eTag:g,config:A}}}/**
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
 */function Ns(e,t){return new Promise((n,r)=>{const a=Math.max(t-Date.now(),0),s=setTimeout(n,a);e.addEventListener(()=>{clearTimeout(s),r(m.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function vs(e){if(!(e instanceof Tt)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class Bs{constructor(t,n){this.client=t,this.storage=n}async fetch(t){const n=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(t,n)}async attemptFetch(t,{throttleEndTimeMillis:n,backoffCount:r}){await Ns(t.signal,n);try{const a=await this.client.fetch(t);return await this.storage.deleteThrottleMetadata(),a}catch(a){if(!vs(a))throw a;const s={throttleEndTimeMillis:Date.now()+Ka(r),backoffCount:r+1};return await this.storage.setThrottleMetadata(s),this.attemptFetch(t,s)}}}/**
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
 */const Ks=60*1e3,Vs=12*60*60*1e3;class Hs{get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}constructor(t,n,r,a,s){this.app=t,this._client=n,this._storageCache=r,this._storage=a,this._logger=s,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:Ks,minimumFetchIntervalMillis:Vs},this.defaultConfig={}}}/**
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
 */function v(e,t){const n=e.target.error||void 0;return m.create(t,{originalErrorMessage:n&&(n==null?void 0:n.message)})}const S="app_namespace_store",xs="firebase_remote_config",Us=1;function js(){return new Promise((e,t)=>{try{const n=indexedDB.open(xs,Us);n.onerror=r=>{t(v(r,"storage-open"))},n.onsuccess=r=>{e(r.target.result)},n.onupgradeneeded=r=>{const a=r.target.result;switch(r.oldVersion){case 0:a.createObjectStore(S,{keyPath:"compositeKey"})}}}catch(n){t(m.create("storage-open",{originalErrorMessage:n==null?void 0:n.message}))}})}class Gt{getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(t){return this.set("last_fetch_status",t)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(t){return this.set("last_successful_fetch_timestamp_millis",t)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(t){return this.set("last_successful_fetch_response",t)}getActiveConfig(){return this.get("active_config")}setActiveConfig(t){return this.set("active_config",t)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(t){return this.set("active_config_etag",t)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(t){return this.set("throttle_metadata",t)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}getCustomSignals(){return this.get("custom_signals")}}class Gs extends Gt{constructor(t,n,r,a=js()){super(),this.appId=t,this.appName=n,this.namespace=r,this.openDbPromise=a}async setCustomSignals(t){const r=(await this.openDbPromise).transaction([S],"readwrite"),a=await this.getWithTransaction("custom_signals",r),s=qt(t,a||{});return await this.setWithTransaction("custom_signals",s,r),s}async getWithTransaction(t,n){return new Promise((r,a)=>{const s=n.objectStore(S),i=this.createCompositeKey(t);try{const o=s.get(i);o.onerror=c=>{a(v(c,"storage-get"))},o.onsuccess=c=>{const l=c.target.result;r(l?l.value:void 0)}}catch(o){a(m.create("storage-get",{originalErrorMessage:o==null?void 0:o.message}))}})}async setWithTransaction(t,n,r){return new Promise((a,s)=>{const i=r.objectStore(S),o=this.createCompositeKey(t);try{const c=i.put({compositeKey:o,value:n});c.onerror=l=>{s(v(l,"storage-set"))},c.onsuccess=()=>{a()}}catch(c){s(m.create("storage-set",{originalErrorMessage:c==null?void 0:c.message}))}})}async get(t){const r=(await this.openDbPromise).transaction([S],"readonly");return this.getWithTransaction(t,r)}async set(t,n){const a=(await this.openDbPromise).transaction([S],"readwrite");return this.setWithTransaction(t,n,a)}async delete(t){const n=await this.openDbPromise;return new Promise((r,a)=>{const i=n.transaction([S],"readwrite").objectStore(S),o=this.createCompositeKey(t);try{const c=i.delete(o);c.onerror=l=>{a(v(l,"storage-delete"))},c.onsuccess=()=>{r()}}catch(c){a(m.create("storage-delete",{originalErrorMessage:c==null?void 0:c.message}))}})}createCompositeKey(t){return[this.appId,this.appName,this.namespace,t].join()}}class qs extends Gt{constructor(){super(...arguments),this.storage={}}async get(t){return Promise.resolve(this.storage[t])}async set(t,n){return this.storage[t]=n,Promise.resolve(void 0)}async delete(t){return this.storage[t]=void 0,Promise.resolve()}async setCustomSignals(t){const n=this.storage.custom_signals||{};return this.storage.custom_signals=qt(t,n),Promise.resolve(this.storage.custom_signals)}}function qt(e,t){const n=Object.assign(Object.assign({},t),e),r=Object.fromEntries(Object.entries(n).filter(([a,s])=>s!==null).map(([a,s])=>typeof s=="number"?[a,s.toString()]:[a,s]));if(Object.keys(r).length>Ge)throw m.create("custom-signal-max-allowed-signals",{maxSignals:Ge});return r}/**
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
 */class Ws{constructor(t){this.storage=t}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}getCustomSignals(){return this.customSignals}async loadFromStorage(){const t=this.storage.getLastFetchStatus(),n=this.storage.getLastSuccessfulFetchTimestampMillis(),r=this.storage.getActiveConfig(),a=this.storage.getCustomSignals(),s=await t;s&&(this.lastFetchStatus=s);const i=await n;i&&(this.lastSuccessfulFetchTimestampMillis=i);const o=await r;o&&(this.activeConfig=o);const c=await a;c&&(this.customSignals=c)}setLastFetchStatus(t){return this.lastFetchStatus=t,this.storage.setLastFetchStatus(t)}setLastSuccessfulFetchTimestampMillis(t){return this.lastSuccessfulFetchTimestampMillis=t,this.storage.setLastSuccessfulFetchTimestampMillis(t)}setActiveConfig(t){return this.activeConfig=t,this.storage.setActiveConfig(t)}async setCustomSignals(t){this.customSignals=await this.storage.setCustomSignals(t)}}/**
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
 */function zs(){E(new Ha(Ls,e,"PUBLIC").setMultipleInstances(!0)),I(ne,je),I(ne,je,"esm2017");function e(t,{options:n}){const r=t.getProvider("app").getImmediate(),a=t.getProvider("installations-internal").getImmediate(),{projectId:s,apiKey:i,appId:o}=r.options;if(!s)throw m.create("registration-project-id");if(!i)throw m.create("registration-api-key");if(!o)throw m.create("registration-app-id");const c=(n==null?void 0:n.templateId)||"firebase",l=ka()?new Gs(o,r.name,c):new qs,h=new Ws(l),d=new ce(ne);d.logLevel=u.ERROR;const f=new Ms(a,rr,c,s,i,o),g=new Bs(f,l),A=new Ps(g,l,h,d),w=new Hs(r,A,h,l,d);return $s(w),w}}zs();const Ys=e=>Object.fromEntries(new URLSearchParams(e)),Js=()=>{const e=zt(),t=Ys(e.search);return"utm_campaign"in t&&"utm_medium"in t&&"utm_source"in t?{traffic_campaign:t.utm_campaign,traffic_medium:t.utm_medium,traffic_source:t.utm_source}:{}},si=()=>{const e=Js();return{logEvent:Wt.useCallback((n,r)=>{},[e])}};var Xs=(e=>(e.CLICKED_BOOKING="hasClickedBooking",e.CLICKED_CANCELED_SELECTED_OFFERS="hasClickedCancelOffers",e.CLICKED_DISABLED_SELECTED_OFFERS="hasClickedDisabledOffers",e.CLICKED_CONSULT_CGU="hasClickedConsultCGU",e.CLICKED_CONSULT_SUPPORT="hasClickedConsultSupport",e.CLICKED_CREATE_ACCOUNT="hasClickedCreateAccount",e.CLICKED_CREATE_VENUE="hasClickedCreateVenue",e.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL="hasClickedSeeLaterFromSuccessVenueCreationModal",e.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL="hasClickedSeeLaterFromSuccessOfferCreationModal",e.CLICKED_SAVE_VENUE="hasClickedSaveVenue",e.CLICKED_DOWNLOAD_BOOKINGS="hasClickedDownloadBooking",e.CLICKED_DOWNLOAD_BOOKINGS_CSV="hasClickedDownloadBookingCsv",e.CLICKED_DOWNLOAD_BOOKINGS_XLS="hasClickedDownloadBookingXls",e.CLICKED_EDIT_PROFILE="hasClickedEditProfile",e.CLICKED_EDIT_COLLECTIVE_OFFER="hasClickedEditCollectiveOffer",e.CLICKED_HOME_STATS_PENDING_OFFERS_FAQ="hasClickedHomeStatsPendingOffersFaq",e.CLICKED_FORGOTTEN_PASSWORD="hasClickedForgottenPassword",e.CLICKED_HELP_CENTER="hasClickedHelpCenter",e.CLICKED_HOME="hasClickedHome",e.CLICKED_LOGOUT="hasClickedLogout",e.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER="hasClickedConfirmedAddHeadlineOffer",e.CLICKED_DISCOVERED_HEADLINE_OFFER="hasClickedDiscoveredHeadlineOffer",e.CLICKED_OFFER="hasClickedOffer",e.CLICKED_OFFER_FORM_NAVIGATION="hasClickedOfferFormNavigation",e.CLICKED_ONBOARDING_FORM_NAVIGATION="HasClickedOnboardingFormNavigation",e.CLICKED_CANCEL_OFFER_CREATION="hasClickedCancelOfferCreation",e.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK="hasClickedPartnerBlockPreviewVenueLink",e.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK="hasClickedPartnerBlockCopyVenueLink",e.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK="hasClickedPartnerBlockDmsApplicationLink",e.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK="hasClickedPartnerBlockCollectiveHelpLink",e.CLICKED_PERSONAL_DATA="hasClickedConsultPersonalData",e.CLICKED_PRO="hasClickedPro",e.CLICKED_REIMBURSEMENT="hasClickedReimbursement",e.CLICKED_SHOW_BOOKINGS="hasClickedShowBooking",e.CLICKED_STATS="hasClickedOffererStats",e.CLICKED_TICKET="hasClickedTicket",e.CLICKED_DUPLICATE_TEMPLATE_OFFER="hasClickedDuplicateTemplateOffer",e.CLICKED_DUPLICATE_BOOKABLE_OFFER="hasClickedDuplicateBookableOffer",e.CLICKED_BEST_PRACTICES_STUDIES="hasClickedBestPracticesAndStudies",e.CLICKED_HELP_LINK="hasClickedHelpLink",e.CLICKED_RESET_FILTERS="hasClickedResetFilter",e.CLICKED_SHOW_STATUS_FILTER="hasClickedShowStatusFilter",e.CLICKED_OMNI_SEARCH_CRITERIA="hasClickedOmniSearchCriteria",e.CLICKED_PAGINATION_NEXT_PAGE="hasClickedPaginationNextPage",e.CLICKED_PAGINATION_PREVIOUS_PAGE="hasClickedPaginationPreviousPage",e.CLICKED_CONTACT_OUR_TEAMS="hasClickedContactOurTeams",e.CLICKED_ARCHIVE_COLLECTIVE_OFFER="hasClickedArchiveCollectiveOffer",e.CLICKED_SAVE_DRAFT_AND_EXIT_COLLECTIVE_OFFER="hasClickedSaveDraftAndExitCollectiveOffer",e.CLICKED_SEE_TEMPLATE_OFFER_EXAMPLE="hasClickedSeeTemplateOfferExample",e.FIRST_LOGIN="firstLogin",e.PAGE_VIEW="page_view",e.SIGNUP_FORM_ABORT="signupFormAbort",e.SIGNUP_FORM_SUCCESS="signupFormSuccess",e.TUTO_PAGE_VIEW="tutoPageView",e.DELETE_DRAFT_OFFER="DeleteDraftOffer",e.CLICKED_NO_VENUE="hasClickedNoVenue",e.CLICKED_EAC_DMS_TIMELINE="hasClickedEacDmsTimeline",e.CLICKED_EAC_DMS_LINK="hasClickedEacDmsLink",e.CLICKED_CREATE_OFFER_FROM_REQUEST="hasClickedCreateOfferFromRequest",e.CLICKED_ADD_IMAGE="hasClickedAddImage",e.DRAG_OR_SELECTED_IMAGE="hasDragOrSelectedImage",e.CLICKED_SAVE_IMAGE="hasClickedSaveImage",e.CLICKED_DELETE_STOCK="hasClickedDeleteStock",e.CLICKED_BULK_DELETE_STOCK="hasClickedBulkDeleteStock",e.CLICKED_DOWNLOAD_OFFER_BOOKINGS="hasDownloadedBookings",e.CLICKED_PAGE_FOR_APP_HOME="hasClickedPageForAppHome",e.CLICKED_PAGE_FOR_ADAGE_HOME="hasClickedPageForAdageHome",e.CLICKED_INVOICES_DOWNLOAD="hasClickedInvoicesDownload",e.CLICKED_PUBLISH_FUTURE_OFFER_EARLIER="hasClickedPublishFutureOfferEarlier",e.EXTRA_PRO_DATA="extra_pro_data",e.CLICKED_NEW_EVOLUTIONS="hasClickedNewEvolutions",e.CLICKED_CONSULT_HELP="hasClickedConsultHelp",e.UPDATED_BOOKING_LIMIT_DATE="hasUpdatedBookingLimitDate",e.CLICKED_GENERATE_TEMPLATE_DESCRIPTION="hasClickedGenerateTemplateDescription",e.UPDATED_EVENT_STOCK_FILTERS="hasUpdatedEventStockFilters",e.CLICKED_VALIDATE_ADD_RECURRENCE_DATES="hasClickedValidateAddRecurrenceDates",e.FAKE_DOOR_VIDEO_INTERESTED="fakeDoorVideoInterested",e.CLICKED_SORT_STOCKS_TABLE="hasClickedSortStocksTable",e))(Xs||{});export{Xs as E,si as u};
