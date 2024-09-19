import{j as v}from"./jsx-runtime-Nms4Y4qS.js";import{K as gt}from"./index-DW7ZRdAf.js";import{r as mt}from"./index-BwDkhjyp.js";import"./config-BdqymTTq.js";import{u as Ct}from"./index-DS_b8lb9.js";import{f as _t}from"./full-help-Co3hxUDJ.js";import{S as Et}from"./SvgIcon-Cibea2Sc.js";import"./_commonjsHelpers-BosuxZz1.js";import"./index-CReuRBEY.js";/**
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
 */const Pe=function(e){const t=[];let r=0;for(let n=0;n<e.length;n++){let a=e.charCodeAt(n);a<128?t[r++]=a:a<2048?(t[r++]=a>>6|192,t[r++]=a&63|128):(a&64512)===55296&&n+1<e.length&&(e.charCodeAt(n+1)&64512)===56320?(a=65536+((a&1023)<<10)+(e.charCodeAt(++n)&1023),t[r++]=a>>18|240,t[r++]=a>>12&63|128,t[r++]=a>>6&63|128,t[r++]=a&63|128):(t[r++]=a>>12|224,t[r++]=a>>6&63|128,t[r++]=a&63|128)}return t},It=function(e){const t=[];let r=0,n=0;for(;r<e.length;){const a=e[r++];if(a<128)t[n++]=String.fromCharCode(a);else if(a>191&&a<224){const s=e[r++];t[n++]=String.fromCharCode((a&31)<<6|s&63)}else if(a>239&&a<365){const s=e[r++],i=e[r++],o=e[r++],c=((a&7)<<18|(s&63)<<12|(i&63)<<6|o&63)-65536;t[n++]=String.fromCharCode(55296+(c>>10)),t[n++]=String.fromCharCode(56320+(c&1023))}else{const s=e[r++],i=e[r++];t[n++]=String.fromCharCode((a&15)<<12|(s&63)<<6|i&63)}}return t.join("")},bt={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(e,t){if(!Array.isArray(e))throw Error("encodeByteArray takes an array as a parameter");this.init_();const r=t?this.byteToCharMapWebSafe_:this.byteToCharMap_,n=[];for(let a=0;a<e.length;a+=3){const s=e[a],i=a+1<e.length,o=i?e[a+1]:0,c=a+2<e.length,l=c?e[a+2]:0,h=s>>2,d=(s&3)<<4|o>>4;let f=(o&15)<<2|l>>6,p=l&63;c||(p=64,i||(f=64)),n.push(r[h],r[d],r[f],r[p])}return n.join("")},encodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?btoa(e):this.encodeByteArray(Pe(e),t)},decodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?atob(e):It(this.decodeStringToByteArray(e,t))},decodeStringToByteArray(e,t){this.init_();const r=t?this.charToByteMapWebSafe_:this.charToByteMap_,n=[];for(let a=0;a<e.length;){const s=r[e.charAt(a++)],o=a<e.length?r[e.charAt(a)]:0;++a;const l=a<e.length?r[e.charAt(a)]:64;++a;const d=a<e.length?r[e.charAt(a)]:64;if(++a,s==null||o==null||l==null||d==null)throw new wt;const f=s<<2|o>>4;if(n.push(f),l!==64){const p=o<<4&240|l>>2;if(n.push(p),d!==64){const b=l<<6&192|d;n.push(b)}}}return n},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let e=0;e<this.ENCODED_VALS.length;e++)this.byteToCharMap_[e]=this.ENCODED_VALS.charAt(e),this.charToByteMap_[this.byteToCharMap_[e]]=e,this.byteToCharMapWebSafe_[e]=this.ENCODED_VALS_WEBSAFE.charAt(e),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[e]]=e,e>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(e)]=e,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(e)]=e)}}};class wt extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const yt=function(e){const t=Pe(e);return bt.encodeByteArray(t,!0)},ke=function(e){return yt(e).replace(/\./g,"")};function Tt(){try{return typeof indexedDB=="object"}catch{return!1}}function St(){return new Promise((e,t)=>{try{let r=!0;const n="validate-browser-context-for-indexeddb-analytics-module",a=self.indexedDB.open(n);a.onsuccess=()=>{a.result.close(),r||self.indexedDB.deleteDatabase(n),e(!0)},a.onupgradeneeded=()=>{r=!1},a.onerror=()=>{var s;t(((s=a.error)===null||s===void 0?void 0:s.message)||"")}}catch(r){t(r)}})}/**
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
 */const At="FirebaseError";let te=class Ne extends Error{constructor(t,r,n){super(r),this.code=t,this.customData=n,this.name=At,Object.setPrototypeOf(this,Ne.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,Be.prototype.create)}},Be=class{constructor(t,r,n){this.service=t,this.serviceName=r,this.errors=n}create(t,...r){const n=r[0]||{},a=`${this.service}/${t}`,s=this.errors[t],i=s?Dt(s,n):"Error",o=`${this.serviceName}: ${i} (${a}).`;return new te(a,o,n)}};function Dt(e,t){return e.replace(Ot,(r,n)=>{const a=t[n];return a!=null?String(a):`<${n}?>`})}const Ot=/\{\$([^}]+)}/g;let Y=class{constructor(t,r,n){this.name=t,this.instanceFactory=r,this.type=n,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}};/**
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
 */var u;(function(e){e[e.DEBUG=0]="DEBUG",e[e.VERBOSE=1]="VERBOSE",e[e.INFO=2]="INFO",e[e.WARN=3]="WARN",e[e.ERROR=4]="ERROR",e[e.SILENT=5]="SILENT"})(u||(u={}));const Lt={debug:u.DEBUG,verbose:u.VERBOSE,info:u.INFO,warn:u.WARN,error:u.ERROR,silent:u.SILENT},Rt=u.INFO,vt={[u.DEBUG]:"log",[u.VERBOSE]:"log",[u.INFO]:"info",[u.WARN]:"warn",[u.ERROR]:"error"},Ft=(e,t,...r)=>{if(t<e.logLevel)return;const n=new Date().toISOString(),a=vt[t];if(a)console[a](`[${n}]  ${e.name}:`,...r);else throw new Error(`Attempted to log a message with an invalid logType (value: ${t})`)};class re{constructor(t){this.name=t,this._logLevel=Rt,this._logHandler=Ft,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(t){if(!(t in u))throw new TypeError(`Invalid value "${t}" assigned to \`logLevel\``);this._logLevel=t}setLogLevel(t){this._logLevel=typeof t=="string"?Lt[t]:t}get logHandler(){return this._logHandler}set logHandler(t){if(typeof t!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=t}get userLogHandler(){return this._userLogHandler}set userLogHandler(t){this._userLogHandler=t}debug(...t){this._userLogHandler&&this._userLogHandler(this,u.DEBUG,...t),this._logHandler(this,u.DEBUG,...t)}log(...t){this._userLogHandler&&this._userLogHandler(this,u.VERBOSE,...t),this._logHandler(this,u.VERBOSE,...t)}info(...t){this._userLogHandler&&this._userLogHandler(this,u.INFO,...t),this._logHandler(this,u.INFO,...t)}warn(...t){this._userLogHandler&&this._userLogHandler(this,u.WARN,...t),this._logHandler(this,u.WARN,...t)}error(...t){this._userLogHandler&&this._userLogHandler(this,u.ERROR,...t),this._logHandler(this,u.ERROR,...t)}}const Mt=(e,t)=>t.some(r=>e instanceof r);let he,de;function Pt(){return he||(he=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function kt(){return de||(de=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const $e=new WeakMap,X=new WeakMap,Ke=new WeakMap,H=new WeakMap,ne=new WeakMap;function Nt(e){const t=new Promise((r,n)=>{const a=()=>{e.removeEventListener("success",s),e.removeEventListener("error",i)},s=()=>{r(y(e.result)),a()},i=()=>{n(e.error),a()};e.addEventListener("success",s),e.addEventListener("error",i)});return t.then(r=>{r instanceof IDBCursor&&$e.set(r,e)}).catch(()=>{}),ne.set(t,e),t}function Bt(e){if(X.has(e))return;const t=new Promise((r,n)=>{const a=()=>{e.removeEventListener("complete",s),e.removeEventListener("error",i),e.removeEventListener("abort",i)},s=()=>{r(),a()},i=()=>{n(e.error||new DOMException("AbortError","AbortError")),a()};e.addEventListener("complete",s),e.addEventListener("error",i),e.addEventListener("abort",i)});X.set(e,t)}let J={get(e,t,r){if(e instanceof IDBTransaction){if(t==="done")return X.get(e);if(t==="objectStoreNames")return e.objectStoreNames||Ke.get(e);if(t==="store")return r.objectStoreNames[1]?void 0:r.objectStore(r.objectStoreNames[0])}return y(e[t])},set(e,t,r){return e[t]=r,!0},has(e,t){return e instanceof IDBTransaction&&(t==="done"||t==="store")?!0:t in e}};function $t(e){J=e(J)}function Kt(e){return e===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(t,...r){const n=e.call(V(this),t,...r);return Ke.set(n,t.sort?t.sort():[t]),y(n)}:kt().includes(e)?function(...t){return e.apply(V(this),t),y($e.get(this))}:function(...t){return y(e.apply(V(this),t))}}function xt(e){return typeof e=="function"?Kt(e):(e instanceof IDBTransaction&&Bt(e),Mt(e,Pt())?new Proxy(e,J):e)}function y(e){if(e instanceof IDBRequest)return Nt(e);if(H.has(e))return H.get(e);const t=xt(e);return t!==e&&(H.set(e,t),ne.set(t,e)),t}const V=e=>ne.get(e);function xe(e,t,{blocked:r,upgrade:n,blocking:a,terminated:s}={}){const i=indexedDB.open(e,t),o=y(i);return n&&i.addEventListener("upgradeneeded",c=>{n(y(i.result),c.oldVersion,c.newVersion,y(i.transaction),c)}),r&&i.addEventListener("blocked",c=>r(c.oldVersion,c.newVersion,c)),o.then(c=>{s&&c.addEventListener("close",()=>s()),a&&c.addEventListener("versionchange",l=>a(l.oldVersion,l.newVersion,l))}).catch(()=>{}),o}const Ht=["get","getKey","getAll","getAllKeys","count"],Vt=["put","add","delete","clear"],U=new Map;function fe(e,t){if(!(e instanceof IDBDatabase&&!(t in e)&&typeof t=="string"))return;if(U.get(t))return U.get(t);const r=t.replace(/FromIndex$/,""),n=t!==r,a=Vt.includes(r);if(!(r in(n?IDBIndex:IDBObjectStore).prototype)||!(a||Ht.includes(r)))return;const s=async function(i,...o){const c=this.transaction(i,a?"readwrite":"readonly");let l=c.store;return n&&(l=l.index(o.shift())),(await Promise.all([l[r](...o),a&&c.done]))[0]};return U.set(t,s),s}$t(e=>({...e,get:(t,r,n)=>fe(t,r)||e.get(t,r,n),has:(t,r)=>!!fe(t,r)||e.has(t,r)}));/**
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
 */class Ut{constructor(t){this.container=t}getPlatformInfoString(){return this.container.getProviders().map(r=>{if(jt(r)){const n=r.getImmediate();return`${n.library}/${n.version}`}else return null}).filter(r=>r).join(" ")}}function jt(e){const t=e.getComponent();return(t==null?void 0:t.type)==="VERSION"}const Q="@firebase/app",pe="0.10.10";/**
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
 */const I=new re("@firebase/app"),Gt="@firebase/app-compat",Wt="@firebase/analytics-compat",qt="@firebase/analytics",zt="@firebase/app-check-compat",Yt="@firebase/app-check",Xt="@firebase/auth",Jt="@firebase/auth-compat",Qt="@firebase/database",Zt="@firebase/database-compat",er="@firebase/functions",tr="@firebase/functions-compat",rr="@firebase/installations",nr="@firebase/installations-compat",ar="@firebase/messaging",sr="@firebase/messaging-compat",ir="@firebase/performance",or="@firebase/performance-compat",cr="@firebase/remote-config",lr="@firebase/remote-config-compat",ur="@firebase/storage",hr="@firebase/storage-compat",dr="@firebase/firestore",fr="@firebase/vertexai-preview",pr="@firebase/firestore-compat",gr="firebase",mr="10.13.1",Cr={[Q]:"fire-core",[Gt]:"fire-core-compat",[qt]:"fire-analytics",[Wt]:"fire-analytics-compat",[Yt]:"fire-app-check",[zt]:"fire-app-check-compat",[Xt]:"fire-auth",[Jt]:"fire-auth-compat",[Qt]:"fire-rtdb",[Zt]:"fire-rtdb-compat",[er]:"fire-fn",[tr]:"fire-fn-compat",[rr]:"fire-iid",[nr]:"fire-iid-compat",[ar]:"fire-fcm",[sr]:"fire-fcm-compat",[ir]:"fire-perf",[or]:"fire-perf-compat",[cr]:"fire-rc",[lr]:"fire-rc-compat",[ur]:"fire-gcs",[hr]:"fire-gcs-compat",[dr]:"fire-fst",[pr]:"fire-fst-compat",[fr]:"fire-vertex","fire-js":"fire-js",[gr]:"fire-js-all"};/**
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
 */const _r=new Map,Er=new Map,ge=new Map;function me(e,t){try{e.container.addComponent(t)}catch(r){I.debug(`Component ${t.name} failed to register with FirebaseApp ${e.name}`,r)}}function T(e){const t=e.name;if(ge.has(t))return I.debug(`There were multiple attempts to register component ${t}.`),!1;ge.set(t,e);for(const r of _r.values())me(r,e);for(const r of Er.values())me(r,e);return!0}function He(e,t){const r=e.container.getProvider("heartbeat").getImmediate({optional:!0});return r&&r.triggerHeartbeat(),e.container.getProvider(t)}/**
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
 */const Ir={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},ae=new Be("app","Firebase",Ir);/**
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
 */const br=mr;function E(e,t,r){var n;let a=(n=Cr[e])!==null&&n!==void 0?n:e;r&&(a+=`-${r}`);const s=a.match(/\s|\//),i=t.match(/\s|\//);if(s||i){const o=[`Unable to register library "${a}" with version "${t}":`];s&&o.push(`library name "${a}" contains illegal characters (whitespace or "/")`),s&&i&&o.push("and"),i&&o.push(`version name "${t}" contains illegal characters (whitespace or "/")`),I.warn(o.join(" "));return}T(new Y(`${a}-version`,()=>({library:a,version:t}),"VERSION"))}/**
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
 */const wr="firebase-heartbeat-database",yr=1,M="firebase-heartbeat-store";let j=null;function Ve(){return j||(j=xe(wr,yr,{upgrade:(e,t)=>{switch(t){case 0:try{e.createObjectStore(M)}catch(r){console.warn(r)}}}}).catch(e=>{throw ae.create("idb-open",{originalErrorMessage:e.message})})),j}async function Tr(e){try{const r=(await Ve()).transaction(M),n=await r.objectStore(M).get(Ue(e));return await r.done,n}catch(t){if(t instanceof te)I.warn(t.message);else{const r=ae.create("idb-get",{originalErrorMessage:t==null?void 0:t.message});I.warn(r.message)}}}async function Ce(e,t){try{const n=(await Ve()).transaction(M,"readwrite");await n.objectStore(M).put(t,Ue(e)),await n.done}catch(r){if(r instanceof te)I.warn(r.message);else{const n=ae.create("idb-set",{originalErrorMessage:r==null?void 0:r.message});I.warn(n.message)}}}function Ue(e){return`${e.name}!${e.options.appId}`}/**
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
 */const Sr=1024,Ar=30*24*60*60*1e3;class Dr{constructor(t){this.container=t,this._heartbeatsCache=null;const r=this.container.getProvider("app").getImmediate();this._storage=new Lr(r),this._heartbeatsCachePromise=this._storage.read().then(n=>(this._heartbeatsCache=n,n))}async triggerHeartbeat(){var t,r;try{const a=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),s=_e();return((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,((r=this._heartbeatsCache)===null||r===void 0?void 0:r.heartbeats)==null)||this._heartbeatsCache.lastSentHeartbeatDate===s||this._heartbeatsCache.heartbeats.some(i=>i.date===s)?void 0:(this._heartbeatsCache.heartbeats.push({date:s,agent:a}),this._heartbeatsCache.heartbeats=this._heartbeatsCache.heartbeats.filter(i=>{const o=new Date(i.date).valueOf();return Date.now()-o<=Ar}),this._storage.overwrite(this._heartbeatsCache))}catch(n){I.warn(n)}}async getHeartbeatsHeader(){var t;try{if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null||this._heartbeatsCache.heartbeats.length===0)return"";const r=_e(),{heartbeatsToSend:n,unsentEntries:a}=Or(this._heartbeatsCache.heartbeats),s=ke(JSON.stringify({version:2,heartbeats:n}));return this._heartbeatsCache.lastSentHeartbeatDate=r,a.length>0?(this._heartbeatsCache.heartbeats=a,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),s}catch(r){return I.warn(r),""}}}function _e(){return new Date().toISOString().substring(0,10)}function Or(e,t=Sr){const r=[];let n=e.slice();for(const a of e){const s=r.find(i=>i.agent===a.agent);if(s){if(s.dates.push(a.date),Ee(r)>t){s.dates.pop();break}}else if(r.push({agent:a.agent,dates:[a.date]}),Ee(r)>t){r.pop();break}n=n.slice(1)}return{heartbeatsToSend:r,unsentEntries:n}}class Lr{constructor(t){this.app=t,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return Tt()?St().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const r=await Tr(this.app);return r!=null&&r.heartbeats?r:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(t){var r;if(await this._canUseIndexedDBPromise){const a=await this.read();return Ce(this.app,{lastSentHeartbeatDate:(r=t.lastSentHeartbeatDate)!==null&&r!==void 0?r:a.lastSentHeartbeatDate,heartbeats:t.heartbeats})}else return}async add(t){var r;if(await this._canUseIndexedDBPromise){const a=await this.read();return Ce(this.app,{lastSentHeartbeatDate:(r=t.lastSentHeartbeatDate)!==null&&r!==void 0?r:a.lastSentHeartbeatDate,heartbeats:[...a.heartbeats,...t.heartbeats]})}else return}}function Ee(e){return ke(JSON.stringify({version:2,heartbeats:e})).length}/**
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
 */function Rr(e){T(new Y("platform-logger",t=>new Ut(t),"PRIVATE")),T(new Y("heartbeat",t=>new Dr(t),"PRIVATE")),E(Q,pe,e),E(Q,pe,"esm2017"),E("fire-js","")}Rr("");function vr(){const e=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof e=="object"&&e.id!==void 0}function je(){try{return typeof indexedDB=="object"}catch{return!1}}function Fr(){return new Promise((e,t)=>{try{let r=!0;const n="validate-browser-context-for-indexeddb-analytics-module",a=self.indexedDB.open(n);a.onsuccess=()=>{a.result.close(),r||self.indexedDB.deleteDatabase(n),e(!0)},a.onupgradeneeded=()=>{r=!1},a.onerror=()=>{var s;t(((s=a.error)===null||s===void 0?void 0:s.message)||"")}}catch(r){t(r)}})}function Mr(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
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
 */const Pr="FirebaseError";class L extends Error{constructor(t,r,n){super(r),this.code=t,this.customData=n,this.name=Pr,Object.setPrototypeOf(this,L.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,$.prototype.create)}}class ${constructor(t,r,n){this.service=t,this.serviceName=r,this.errors=n}create(t,...r){const n=r[0]||{},a=`${this.service}/${t}`,s=this.errors[t],i=s?kr(s,n):"Error",o=`${this.serviceName}: ${i} (${a}).`;return new L(a,o,n)}}function kr(e,t){return e.replace(Nr,(r,n)=>{const a=t[n];return a!=null?String(a):`<${n}?>`})}const Nr=/\{\$([^}]+)}/g;/**
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
 */const Br=1e3,$r=2,Kr=4*60*60*1e3,xr=.5;function Z(e,t=Br,r=$r){const n=t*Math.pow(r,e),a=Math.round(xr*n*(Math.random()-.5)*2);return Math.min(Kr,n+a)}/**
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
 */function Ge(e){return e&&e._delegate?e._delegate:e}class P{constructor(t,r,n){this.name=t,this.instanceFactory=r,this.type=n,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}}const We="@firebase/installations",se="0.6.9";/**
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
 */const qe=1e4,ze=`w:${se}`,Ye="FIS_v2",Hr="https://firebaseinstallations.googleapis.com/v1",Vr=60*60*1e3,Ur="installations",jr="Installations";/**
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
 */const Gr={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},D=new $(Ur,jr,Gr);function Xe(e){return e instanceof L&&e.code.includes("request-failed")}/**
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
 */function Je({projectId:e}){return`${Hr}/projects/${e}/installations`}function Qe(e){return{token:e.token,requestStatus:2,expiresIn:qr(e.expiresIn),creationTime:Date.now()}}async function Ze(e,t){const n=(await t.json()).error;return D.create("request-failed",{requestName:e,serverCode:n.code,serverMessage:n.message,serverStatus:n.status})}function et({apiKey:e}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e})}function Wr(e,{refreshToken:t}){const r=et(e);return r.append("Authorization",zr(t)),r}async function tt(e){const t=await e();return t.status>=500&&t.status<600?e():t}function qr(e){return Number(e.replace("s","000"))}function zr(e){return`${Ye} ${e}`}/**
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
 */async function Yr({appConfig:e,heartbeatServiceProvider:t},{fid:r}){const n=Je(e),a=et(e),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&a.append("x-firebase-client",l)}const i={fid:r,authVersion:Ye,appId:e.appId,sdkVersion:ze},o={method:"POST",headers:a,body:JSON.stringify(i)},c=await tt(()=>fetch(n,o));if(c.ok){const l=await c.json();return{fid:l.fid||r,registrationStatus:2,refreshToken:l.refreshToken,authToken:Qe(l.authToken)}}else throw await Ze("Create Installation",c)}/**
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
 */function rt(e){return new Promise(t=>{setTimeout(t,e)})}/**
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
 */function Xr(e){return btoa(String.fromCharCode(...e)).replace(/\+/g,"-").replace(/\//g,"_")}/**
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
 */const Jr=/^[cdef][\w-]{21}$/,ee="";function Qr(){try{const e=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(e),e[0]=112+e[0]%16;const r=Zr(e);return Jr.test(r)?r:ee}catch{return ee}}function Zr(e){return Xr(e).substr(0,22)}/**
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
 */const nt=new Map;function at(e,t){const r=K(e);st(r,t),en(r,t)}function st(e,t){const r=nt.get(e);if(r)for(const n of r)n(t)}function en(e,t){const r=tn();r&&r.postMessage({key:e,fid:t}),rn()}let A=null;function tn(){return!A&&"BroadcastChannel"in self&&(A=new BroadcastChannel("[Firebase] FID Change"),A.onmessage=e=>{st(e.data.key,e.data.fid)}),A}function rn(){nt.size===0&&A&&(A.close(),A=null)}/**
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
 */const nn="firebase-installations-database",an=1,O="firebase-installations-store";let G=null;function ie(){return G||(G=xe(nn,an,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(O)}}})),G}async function B(e,t){const r=K(e),a=(await ie()).transaction(O,"readwrite"),s=a.objectStore(O),i=await s.get(r);return await s.put(t,r),await a.done,(!i||i.fid!==t.fid)&&at(e,t.fid),t}async function it(e){const t=K(e),n=(await ie()).transaction(O,"readwrite");await n.objectStore(O).delete(t),await n.done}async function x(e,t){const r=K(e),a=(await ie()).transaction(O,"readwrite"),s=a.objectStore(O),i=await s.get(r),o=t(i);return o===void 0?await s.delete(r):await s.put(o,r),await a.done,o&&(!i||i.fid!==o.fid)&&at(e,o.fid),o}/**
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
 */async function oe(e){let t;const r=await x(e.appConfig,n=>{const a=sn(n),s=on(e,a);return t=s.registrationPromise,s.installationEntry});return r.fid===ee?{installationEntry:await t}:{installationEntry:r,registrationPromise:t}}function sn(e){const t=e||{fid:Qr(),registrationStatus:0};return ot(t)}function on(e,t){if(t.registrationStatus===0){if(!navigator.onLine){const a=Promise.reject(D.create("app-offline"));return{installationEntry:t,registrationPromise:a}}const r={fid:t.fid,registrationStatus:1,registrationTime:Date.now()},n=cn(e,r);return{installationEntry:r,registrationPromise:n}}else return t.registrationStatus===1?{installationEntry:t,registrationPromise:ln(e)}:{installationEntry:t}}async function cn(e,t){try{const r=await Yr(e,t);return B(e.appConfig,r)}catch(r){throw Xe(r)&&r.customData.serverCode===409?await it(e.appConfig):await B(e.appConfig,{fid:t.fid,registrationStatus:0}),r}}async function ln(e){let t=await Ie(e.appConfig);for(;t.registrationStatus===1;)await rt(100),t=await Ie(e.appConfig);if(t.registrationStatus===0){const{installationEntry:r,registrationPromise:n}=await oe(e);return n||r}return t}function Ie(e){return x(e,t=>{if(!t)throw D.create("installation-not-found");return ot(t)})}function ot(e){return un(e)?{fid:e.fid,registrationStatus:0}:e}function un(e){return e.registrationStatus===1&&e.registrationTime+qe<Date.now()}/**
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
 */async function hn({appConfig:e,heartbeatServiceProvider:t},r){const n=dn(e,r),a=Wr(e,r),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&a.append("x-firebase-client",l)}const i={installation:{sdkVersion:ze,appId:e.appId}},o={method:"POST",headers:a,body:JSON.stringify(i)},c=await tt(()=>fetch(n,o));if(c.ok){const l=await c.json();return Qe(l)}else throw await Ze("Generate Auth Token",c)}function dn(e,{fid:t}){return`${Je(e)}/${t}/authTokens:generate`}/**
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
 */async function ce(e,t=!1){let r;const n=await x(e.appConfig,s=>{if(!ct(s))throw D.create("not-registered");const i=s.authToken;if(!t&&gn(i))return s;if(i.requestStatus===1)return r=fn(e,t),s;{if(!navigator.onLine)throw D.create("app-offline");const o=Cn(s);return r=pn(e,o),o}});return r?await r:n.authToken}async function fn(e,t){let r=await be(e.appConfig);for(;r.authToken.requestStatus===1;)await rt(100),r=await be(e.appConfig);const n=r.authToken;return n.requestStatus===0?ce(e,t):n}function be(e){return x(e,t=>{if(!ct(t))throw D.create("not-registered");const r=t.authToken;return _n(r)?Object.assign(Object.assign({},t),{authToken:{requestStatus:0}}):t})}async function pn(e,t){try{const r=await hn(e,t),n=Object.assign(Object.assign({},t),{authToken:r});return await B(e.appConfig,n),r}catch(r){if(Xe(r)&&(r.customData.serverCode===401||r.customData.serverCode===404))await it(e.appConfig);else{const n=Object.assign(Object.assign({},t),{authToken:{requestStatus:0}});await B(e.appConfig,n)}throw r}}function ct(e){return e!==void 0&&e.registrationStatus===2}function gn(e){return e.requestStatus===2&&!mn(e)}function mn(e){const t=Date.now();return t<e.creationTime||e.creationTime+e.expiresIn<t+Vr}function Cn(e){const t={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},e),{authToken:t})}function _n(e){return e.requestStatus===1&&e.requestTime+qe<Date.now()}/**
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
 */async function En(e){const t=e,{installationEntry:r,registrationPromise:n}=await oe(t);return n?n.catch(console.error):ce(t).catch(console.error),r.fid}/**
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
 */async function In(e,t=!1){const r=e;return await bn(r),(await ce(r,t)).token}async function bn(e){const{registrationPromise:t}=await oe(e);t&&await t}/**
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
 */function wn(e){if(!e||!e.options)throw W("App Configuration");if(!e.name)throw W("App Name");const t=["projectId","apiKey","appId"];for(const r of t)if(!e.options[r])throw W(r);return{appName:e.name,projectId:e.options.projectId,apiKey:e.options.apiKey,appId:e.options.appId}}function W(e){return D.create("missing-app-config-values",{valueName:e})}/**
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
 */const lt="installations",yn="installations-internal",Tn=e=>{const t=e.getProvider("app").getImmediate(),r=wn(t),n=He(t,"heartbeat");return{app:t,appConfig:r,heartbeatServiceProvider:n,_delete:()=>Promise.resolve()}},Sn=e=>{const t=e.getProvider("app").getImmediate(),r=He(t,lt).getImmediate();return{getId:()=>En(r),getToken:a=>In(r,a)}};function An(){T(new P(lt,Tn,"PUBLIC")),T(new P(yn,Sn,"PRIVATE"))}An();E(We,se);E(We,se,"esm2017");/**
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
 */const we="analytics",Dn="firebase_id",On="origin",Ln=60*1e3,Rn="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",le="https://www.googletagmanager.com/gtag/js";/**
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
 */const m=new re("@firebase/analytics");/**
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
 */const vn={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-initialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},C=new $("analytics","Analytics",vn);/**
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
 */function Fn(e){if(!e.startsWith(le)){const t=C.create("invalid-gtag-resource",{gtagURL:e});return m.warn(t.message),""}return e}function ut(e){return Promise.all(e.map(t=>t.catch(r=>r)))}function Mn(e,t){let r;return window.trustedTypes&&(r=window.trustedTypes.createPolicy(e,t)),r}function Pn(e,t){const r=Mn("firebase-js-sdk-policy",{createScriptURL:Fn}),n=document.createElement("script"),a=`${le}?l=${e}&id=${t}`;n.src=r?r==null?void 0:r.createScriptURL(a):a,n.async=!0,document.head.appendChild(n)}function kn(e){let t=[];return Array.isArray(window[e])?t=window[e]:window[e]=t,t}async function Nn(e,t,r,n,a,s){const i=n[a];try{if(i)await t[i];else{const c=(await ut(r)).find(l=>l.measurementId===a);c&&await t[c.appId]}}catch(o){m.error(o)}e("config",a,s)}async function Bn(e,t,r,n,a){try{let s=[];if(a&&a.send_to){let i=a.send_to;Array.isArray(i)||(i=[i]);const o=await ut(r);for(const c of i){const l=o.find(d=>d.measurementId===c),h=l&&t[l.appId];if(h)s.push(h);else{s=[];break}}}s.length===0&&(s=Object.values(t)),await Promise.all(s),e("event",n,a||{})}catch(s){m.error(s)}}function $n(e,t,r,n){async function a(s,...i){try{if(s==="event"){const[o,c]=i;await Bn(e,t,r,o,c)}else if(s==="config"){const[o,c]=i;await Nn(e,t,r,n,o,c)}else if(s==="consent"){const[o,c]=i;e("consent",o,c)}else if(s==="get"){const[o,c,l]=i;e("get",o,c,l)}else if(s==="set"){const[o]=i;e("set",o)}else e(s,...i)}catch(o){m.error(o)}}return a}function Kn(e,t,r,n,a){let s=function(...i){window[n].push(arguments)};return window[a]&&typeof window[a]=="function"&&(s=window[a]),window[a]=$n(s,e,t,r),{gtagCore:s,wrappedGtag:window[a]}}function xn(e){const t=window.document.getElementsByTagName("script");for(const r of Object.values(t))if(r.src&&r.src.includes(le)&&r.src.includes(e))return r;return null}/**
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
 */const Hn=30,Vn=1e3;class Un{constructor(t={},r=Vn){this.throttleMetadata=t,this.intervalMillis=r}getThrottleMetadata(t){return this.throttleMetadata[t]}setThrottleMetadata(t,r){this.throttleMetadata[t]=r}deleteThrottleMetadata(t){delete this.throttleMetadata[t]}}const ht=new Un;function jn(e){return new Headers({Accept:"application/json","x-goog-api-key":e})}async function Gn(e){var t;const{appId:r,apiKey:n}=e,a={method:"GET",headers:jn(n)},s=Rn.replace("{app-id}",r),i=await fetch(s,a);if(i.status!==200&&i.status!==304){let o="";try{const c=await i.json();!((t=c.error)===null||t===void 0)&&t.message&&(o=c.error.message)}catch{}throw C.create("config-fetch-failed",{httpStatus:i.status,responseMessage:o})}return i.json()}async function Wn(e,t=ht,r){const{appId:n,apiKey:a,measurementId:s}=e.options;if(!n)throw C.create("no-app-id");if(!a){if(s)return{measurementId:s,appId:n};throw C.create("no-api-key")}const i=t.getThrottleMetadata(n)||{backoffCount:0,throttleEndTimeMillis:Date.now()},o=new Yn;return setTimeout(async()=>{o.abort()},Ln),dt({appId:n,apiKey:a,measurementId:s},i,o,t)}async function dt(e,{throttleEndTimeMillis:t,backoffCount:r},n,a=ht){var s;const{appId:i,measurementId:o}=e;try{await qn(n,t)}catch(c){if(o)return m.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${o} provided in the "measurementId" field in the local Firebase config. [${c==null?void 0:c.message}]`),{appId:i,measurementId:o};throw c}try{const c=await Gn(e);return a.deleteThrottleMetadata(i),c}catch(c){const l=c;if(!zn(l)){if(a.deleteThrottleMetadata(i),o)return m.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${o} provided in the "measurementId" field in the local Firebase config. [${l==null?void 0:l.message}]`),{appId:i,measurementId:o};throw c}const h=Number((s=l==null?void 0:l.customData)===null||s===void 0?void 0:s.httpStatus)===503?Z(r,a.intervalMillis,Hn):Z(r,a.intervalMillis),d={throttleEndTimeMillis:Date.now()+h,backoffCount:r+1};return a.setThrottleMetadata(i,d),m.debug(`Calling attemptFetch again in ${h} millis`),dt(e,d,n,a)}}function qn(e,t){return new Promise((r,n)=>{const a=Math.max(t-Date.now(),0),s=setTimeout(r,a);e.addEventListener(()=>{clearTimeout(s),n(C.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function zn(e){if(!(e instanceof L)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class Yn{constructor(){this.listeners=[]}addEventListener(t){this.listeners.push(t)}abort(){this.listeners.forEach(t=>t())}}async function Xn(e,t,r,n,a){if(a&&a.global){e("event",r,n);return}else{const s=await t,i=Object.assign(Object.assign({},n),{send_to:s});e("event",r,i)}}/**
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
 */async function Jn(){if(je())try{await Fr()}catch(e){return m.warn(C.create("indexeddb-unavailable",{errorInfo:e==null?void 0:e.toString()}).message),!1}else return m.warn(C.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function Qn(e,t,r,n,a,s,i){var o;const c=Wn(e);c.then(p=>{r[p.measurementId]=p.appId,e.options.measurementId&&p.measurementId!==e.options.measurementId&&m.warn(`The measurement ID in the local Firebase config (${e.options.measurementId}) does not match the measurement ID fetched from the server (${p.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(p=>m.error(p)),t.push(c);const l=Jn().then(p=>{if(p)return n.getId()}),[h,d]=await Promise.all([c,l]);xn(s)||Pn(s,h.measurementId),a("js",new Date);const f=(o=i==null?void 0:i.config)!==null&&o!==void 0?o:{};return f[On]="firebase",f.update=!0,d!=null&&(f[Dn]=d),a("config",h.measurementId,f),h.measurementId}/**
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
 */class Zn{constructor(t){this.app=t}_delete(){return delete F[this.app.options.appId],Promise.resolve()}}let F={},ye=[];const Te={};let q="dataLayer",ea="gtag",Se,ft,Ae=!1;function ta(){const e=[];if(vr()&&e.push("This is a browser extension environment."),Mr()||e.push("Cookies are not available."),e.length>0){const t=e.map((n,a)=>`(${a+1}) ${n}`).join(" "),r=C.create("invalid-analytics-context",{errorInfo:t});m.warn(r.message)}}function ra(e,t,r){ta();const n=e.options.appId;if(!n)throw C.create("no-app-id");if(!e.options.apiKey)if(e.options.measurementId)m.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${e.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw C.create("no-api-key");if(F[n]!=null)throw C.create("already-exists",{id:n});if(!Ae){kn(q);const{wrappedGtag:s,gtagCore:i}=Kn(F,ye,Te,q,ea);ft=s,Se=i,Ae=!0}return F[n]=Qn(e,ye,Te,t,Se,q,r),new Zn(e)}function na(e,t,r,n){e=Ge(e),Xn(ft,F[e.app.options.appId],t,r,n).catch(a=>m.error(a))}const De="@firebase/analytics",Oe="0.10.8";function aa(){T(new P(we,(t,{options:r})=>{const n=t.getProvider("app").getImmediate(),a=t.getProvider("installations-internal").getImmediate();return ra(n,a,r)},"PUBLIC")),T(new P("analytics-internal",e,"PRIVATE")),E(De,Oe),E(De,Oe,"esm2017");function e(t){try{const r=t.getProvider(we).getImmediate();return{logEvent:(n,a,s)=>na(r,n,a,s)}}catch(r){throw C.create("interop-component-reg-failed",{reason:r})}}}aa();const z="@firebase/remote-config",Le="0.4.9";/**
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
 */const sa="remote-config";/**
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
 */const ia={"registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser"},g=new $("remoteconfig","Remote Config",ia);function oa(e){const t=Ge(e);return t._initializePromise||(t._initializePromise=t._storageCache.loadFromStorage().then(()=>{t._isInitializationComplete=!0})),t._initializePromise}/**
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
 */class ca{constructor(t,r,n,a){this.client=t,this.storage=r,this.storageCache=n,this.logger=a}isCachedDataFresh(t,r){if(!r)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const n=Date.now()-r,a=n<=t;return this.logger.debug(`Config fetch cache check. Cache age millis: ${n}. Cache max age millis (minimumFetchIntervalMillis setting): ${t}. Is cache hit: ${a}.`),a}async fetch(t){const[r,n]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(n&&this.isCachedDataFresh(t.cacheMaxAgeMillis,r))return n;t.eTag=n&&n.eTag;const a=await this.client.fetch(t),s=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return a.status===200&&s.push(this.storage.setLastSuccessfulFetchResponse(a)),await Promise.all(s),a}}/**
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
 */function la(e=navigator){return e.languages&&e.languages[0]||e.language}/**
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
 */class ua{constructor(t,r,n,a,s,i){this.firebaseInstallations=t,this.sdkVersion=r,this.namespace=n,this.projectId=a,this.apiKey=s,this.appId=i}async fetch(t){const[r,n]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),s=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,i={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":t.eTag||"*"},o={sdk_version:this.sdkVersion,app_instance_id:r,app_instance_id_token:n,app_id:this.appId,language_code:la()},c={method:"POST",headers:i,body:JSON.stringify(o)},l=fetch(s,c),h=new Promise((_,w)=>{t.signal.addEventListener(()=>{const ue=new Error("The operation was aborted.");ue.name="AbortError",w(ue)})});let d;try{await Promise.race([l,h]),d=await l}catch(_){let w="fetch-client-network";throw(_==null?void 0:_.name)==="AbortError"&&(w="fetch-timeout"),g.create(w,{originalErrorMessage:_==null?void 0:_.message})}let f=d.status;const p=d.headers.get("ETag")||void 0;let b,R;if(d.status===200){let _;try{_=await d.json()}catch(w){throw g.create("fetch-client-parse",{originalErrorMessage:w==null?void 0:w.message})}b=_.entries,R=_.state}if(R==="INSTANCE_STATE_UNSPECIFIED"?f=500:R==="NO_CHANGE"?f=304:(R==="NO_TEMPLATE"||R==="EMPTY_CONFIG")&&(b={}),f!==304&&f!==200)throw g.create("fetch-status",{httpStatus:f});return{status:f,eTag:p,config:b}}}/**
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
 */function ha(e,t){return new Promise((r,n)=>{const a=Math.max(t-Date.now(),0),s=setTimeout(r,a);e.addEventListener(()=>{clearTimeout(s),n(g.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function da(e){if(!(e instanceof L)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class fa{constructor(t,r){this.client=t,this.storage=r}async fetch(t){const r=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(t,r)}async attemptFetch(t,{throttleEndTimeMillis:r,backoffCount:n}){await ha(t.signal,r);try{const a=await this.client.fetch(t);return await this.storage.deleteThrottleMetadata(),a}catch(a){if(!da(a))throw a;const s={throttleEndTimeMillis:Date.now()+Z(n),backoffCount:n+1};return await this.storage.setThrottleMetadata(s),this.attemptFetch(t,s)}}}/**
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
 */const pa=60*1e3,ga=12*60*60*1e3;class ma{constructor(t,r,n,a,s){this.app=t,this._client=r,this._storageCache=n,this._storage=a,this._logger=s,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:pa,minimumFetchIntervalMillis:ga},this.defaultConfig={}}get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}}/**
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
 */function N(e,t){const r=e.target.error||void 0;return g.create(t,{originalErrorMessage:r&&(r==null?void 0:r.message)})}const S="app_namespace_store",Ca="firebase_remote_config",_a=1;function Ea(){return new Promise((e,t)=>{try{const r=indexedDB.open(Ca,_a);r.onerror=n=>{t(N(n,"storage-open"))},r.onsuccess=n=>{e(n.target.result)},r.onupgradeneeded=n=>{const a=n.target.result;switch(n.oldVersion){case 0:a.createObjectStore(S,{keyPath:"compositeKey"})}}}catch(r){t(g.create("storage-open",{originalErrorMessage:r==null?void 0:r.message}))}})}class Ia{constructor(t,r,n,a=Ea()){this.appId=t,this.appName=r,this.namespace=n,this.openDbPromise=a}getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(t){return this.set("last_fetch_status",t)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(t){return this.set("last_successful_fetch_timestamp_millis",t)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(t){return this.set("last_successful_fetch_response",t)}getActiveConfig(){return this.get("active_config")}setActiveConfig(t){return this.set("active_config",t)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(t){return this.set("active_config_etag",t)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(t){return this.set("throttle_metadata",t)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}async get(t){const r=await this.openDbPromise;return new Promise((n,a)=>{const i=r.transaction([S],"readonly").objectStore(S),o=this.createCompositeKey(t);try{const c=i.get(o);c.onerror=l=>{a(N(l,"storage-get"))},c.onsuccess=l=>{const h=l.target.result;n(h?h.value:void 0)}}catch(c){a(g.create("storage-get",{originalErrorMessage:c==null?void 0:c.message}))}})}async set(t,r){const n=await this.openDbPromise;return new Promise((a,s)=>{const o=n.transaction([S],"readwrite").objectStore(S),c=this.createCompositeKey(t);try{const l=o.put({compositeKey:c,value:r});l.onerror=h=>{s(N(h,"storage-set"))},l.onsuccess=()=>{a()}}catch(l){s(g.create("storage-set",{originalErrorMessage:l==null?void 0:l.message}))}})}async delete(t){const r=await this.openDbPromise;return new Promise((n,a)=>{const i=r.transaction([S],"readwrite").objectStore(S),o=this.createCompositeKey(t);try{const c=i.delete(o);c.onerror=l=>{a(N(l,"storage-delete"))},c.onsuccess=()=>{n()}}catch(c){a(g.create("storage-delete",{originalErrorMessage:c==null?void 0:c.message}))}})}createCompositeKey(t){return[this.appId,this.appName,this.namespace,t].join()}}/**
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
 */class ba{constructor(t){this.storage=t}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}async loadFromStorage(){const t=this.storage.getLastFetchStatus(),r=this.storage.getLastSuccessfulFetchTimestampMillis(),n=this.storage.getActiveConfig(),a=await t;a&&(this.lastFetchStatus=a);const s=await r;s&&(this.lastSuccessfulFetchTimestampMillis=s);const i=await n;i&&(this.activeConfig=i)}setLastFetchStatus(t){return this.lastFetchStatus=t,this.storage.setLastFetchStatus(t)}setLastSuccessfulFetchTimestampMillis(t){return this.lastSuccessfulFetchTimestampMillis=t,this.storage.setLastSuccessfulFetchTimestampMillis(t)}setActiveConfig(t){return this.activeConfig=t,this.storage.setActiveConfig(t)}}/**
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
 */function wa(){T(new P(sa,e,"PUBLIC").setMultipleInstances(!0)),E(z,Le),E(z,Le,"esm2017");function e(t,{instanceIdentifier:r}){const n=t.getProvider("app").getImmediate(),a=t.getProvider("installations-internal").getImmediate();if(typeof window>"u")throw g.create("registration-window");if(!je())throw g.create("indexed-db-unavailable");const{projectId:s,apiKey:i,appId:o}=n.options;if(!s)throw g.create("registration-project-id");if(!i)throw g.create("registration-api-key");if(!o)throw g.create("registration-app-id");r=r||"firebase";const c=new Ia(o,n.name,r),l=new ba(c),h=new re(z);h.logLevel=u.ERROR;const d=new ua(a,br,r,s,i,o),f=new fa(d,c),p=new ca(f,c,l,h),b=new ma(n,p,l,c,h);return oa(b),b}}wa();const ya=e=>Object.fromEntries(new URLSearchParams(e)),Ta=()=>{const e=Ct(),t=ya(e.search);return"utm_campaign"in t&&"utm_medium"in t&&"utm_source"in t?{traffic_campaign:t.utm_campaign,traffic_medium:t.utm_medium,traffic_source:t.utm_source}:{}},Sa=()=>{const e=Ta();return{logEvent:mt.useCallback((r,n)=>{},[e])}};var pt=(e=>(e.CLICKED_BOOKING="hasClickedBooking",e.CLICKED_CANCELED_SELECTED_OFFERS="hasClickedCancelOffers",e.CLICKED_DISABLED_SELECTED_OFFERS="hasClickedDisabledOffers",e.CLICKED_CONSULT_CGU="hasClickedConsultCGU",e.CLICKED_CONSULT_SUPPORT="hasClickedConsultSupport",e.CLICKED_CREATE_ACCOUNT="hasClickedCreateAccount",e.CLICKED_CREATE_VENUE="hasClickedCreateVenue",e.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL="hasClickedSeeLaterFromSuccessVenueCreationModal",e.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL="hasClickedSeeLaterFromSuccessOfferCreationModal",e.CLICKED_SAVE_VENUE="hasClickedSaveVenue",e.CLICKED_DOWNLOAD_BOOKINGS="hasClickedDownloadBooking",e.CLICKED_DOWNLOAD_BOOKINGS_CSV="hasClickedDownloadBookingCsv",e.CLICKED_DOWNLOAD_BOOKINGS_XLS="hasClickedDownloadBookingXls",e.CLICKED_EDIT_PROFILE="hasClickedEditProfile",e.CLICKED_EDIT_COLLECTIVE_OFFER="hasClickedEditCollectiveOffer",e.CLICKED_HOME_STATS_PENDING_OFFERS_FAQ="hasClickedHomeStatsPendingOffersFaq",e.CLICKED_FORGOTTEN_PASSWORD="hasClickedForgottenPassword",e.CLICKED_HELP_CENTER="hasClickedHelpCenter",e.CLICKED_HOME="hasClickedHome",e.CLICKED_LOGOUT="hasClickedLogout",e.CLICKED_OFFER="hasClickedOffer",e.CLICKED_OFFER_FORM_NAVIGATION="hasClickedOfferFormNavigation",e.CLICKED_ONBOARDING_FORM_NAVIGATION="HasClickedOnboardingFormNavigation",e.CLICKED_CANCEL_OFFER_CREATION="hasClickedCancelOfferCreation",e.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK="hasClickedPartnerBlockPreviewVenueLink",e.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK="hasClickedPartnerBlockCopyVenueLink",e.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK="hasClickedPartnerBlockDmsApplicationLink",e.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK="hasClickedPartnerBlockCollectiveHelpLink",e.CLICKED_PERSONAL_DATA="hasClickedConsultPersonalData",e.CLICKED_PRO="hasClickedPro",e.CLICKED_REIMBURSEMENT="hasClickedReimbursement",e.CLICKED_SHOW_BOOKINGS="hasClickedShowBooking",e.CLICKED_STATS="hasClickedOffererStats",e.CLICKED_TICKET="hasClickedTicket",e.CLICKED_DUPLICATE_TEMPLATE_OFFER="hasClickedDuplicateTemplateOffer",e.CLICKED_BEST_PRACTICES_STUDIES="hasClickedBestPracticesAndStudies",e.CLICKED_HELP_LINK="hasClickedHelpLink",e.CLICKED_RESET_FILTERS="hasClickedResetFilter",e.CLICKED_SHOW_STATUS_FILTER="hasClickedShowStatusFilter",e.CLICKED_OMNI_SEARCH_CRITERIA="hasClickedOmniSearchCriteria",e.CLICKED_PAGINATION_NEXT_PAGE="hasClickedPaginationNextPage",e.CLICKED_PAGINATION_PREVIOUS_PAGE="hasClickedPaginationPreviousPage",e.CLICKED_CONTACT_OUR_TEAMS="hasClickedContactOurTeams",e.CLICKED_ARCHIVE_COLLECTIVE_OFFER="hasClickedArchiveCollectiveOffer",e.CLICKED_SAVE_DRAFT_AND_EXIT_COLLECTIVE_OFFER="hasClickedSaveDraftAndExitCollectiveOffer",e.FIRST_LOGIN="firstLogin",e.PAGE_VIEW="page_view",e.SIGNUP_FORM_ABORT="signupFormAbort",e.SIGNUP_FORM_SUCCESS="signupFormSuccess",e.TUTO_PAGE_VIEW="tutoPageView",e.DELETE_DRAFT_OFFER="DeleteDraftOffer",e.CLICKED_NO_VENUE="hasClickedNoVenue",e.CLICKED_EAC_DMS_TIMELINE="hasClickedEacDmsTimeline",e.CLICKED_EAC_DMS_LINK="hasClickedEacDmsLink",e.CLICKED_CREATE_OFFER_FROM_REQUEST="hasClickedCreateOfferFromRequest",e.CLICKED_ADD_IMAGE="hasClickedAddImage",e.CLICKED_DELETE_STOCK="hasClickedDeleteStock",e.CLICKED_BULK_DELETE_STOCK="hasClickedBulkDeleteStock",e.CLICKED_DOWNLOAD_OFFER_BOOKINGS="hasDownloadedBookings",e.CLICKED_PAGE_FOR_APP_HOME="hasClickedPageForAppHome",e.CLICKED_PAGE_FOR_ADAGE_HOME="hasClickedPageForAdageHome",e.CLICKED_INVOICES_DOWNLOAD="hasClickedInvoicesDownload",e.CLICKED_PUBLISH_FUTURE_OFFER_EARLIER="hasClickedPublishFutureOfferEarlier",e.EXTRA_PRO_DATA="extra_pro_data",e))(pt||{});const Re={"help-link":"_help-link_1daaj_1","help-link-text":"_help-link-text_1daaj_9"},Aa=()=>{const{logEvent:e}=Sa();return v.jsxs("a",{onClick:()=>e(pt.CLICKED_HELP_LINK,{from:location.pathname}),className:Re["help-link"],href:"https://aide.passculture.app/hc/fr/articles/4411991940369--Acteurs-culturels-Comment-poster-une-offre-%C3%A0-destination-d-un-groupe-scolaire-",rel:"noreferrer",target:"_blank",children:[v.jsx(Et,{src:_t,alt:"",width:"42"}),v.jsx("span",{className:Re["help-link-text"],children:"Aide"})]})},$a={title:"components/HelpLink",component:Aa,decorators:[e=>v.jsx("div",{style:{width:500,height:500},children:v.jsx(e,{})}),gt]},k={};var ve,Fe,Me;k.parameters={...k.parameters,docs:{...(ve=k.parameters)==null?void 0:ve.docs,source:{originalSource:"{}",...(Me=(Fe=k.parameters)==null?void 0:Fe.docs)==null?void 0:Me.source}}};const Ka=["Default"];export{k as Default,Ka as __namedExportsOrder,$a as default};
