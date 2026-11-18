"""Task 4 (Part II): security audit model for a small healthcare test app. Input = manifest/data-store/network/component description; output = STRIDE threats, mechanisms, residual risk, verdict."""
import json,sys
APP={
 "permissions":["INTERNET","CAMERA","ACCESS_FINE_LOCATION","READ_CONTACTS"],
 "runtime_permission_requested_at_use":{"CAMERA":True,"ACCESS_FINE_LOCATION":True,"READ_CONTACTS":False},
 "stores":{"auth_token":"Keystore-wrapped AES-GCM in EncryptedSharedPreferences","appointments_db":"SQLite (SQLCipher, key in Keystore)","photos":"app-private files dir","debug_log":"external storage"},
 "network":[{"host":"api.clinic.example","proto":"https","pinning":True},{"host":"analytics.example","proto":"http","pinning":False}],
 "components":[{"name":"MainActivity","exported":True,"permission":None,"launcher":True},{"name":"PatientRecordActivity","exported":False},{"name":"SyncReceiver","exported":True,"permission":None}],
 "debuggable":False,"allowBackup":True,"min_sdk":26,"signed_v2":True,
}
def audit(app,weaken=None):
    app=json.loads(json.dumps(app))
    if weaken=="token_plain": app["stores"]["auth_token"]="plain SharedPreferences"
    if weaken=="export_record": [c.update(exported=True) for c in app["components"] if c["name"]=="PatientRecordActivity"]
    if weaken=="cleartext": app["network"][0].update(proto="http",pinning=False)
    T=[]  # (id, STRIDE, asset, vector, mechanism, status, residual)
    tok=app["stores"]["auth_token"]
    T.append(("T1","Information disclosure","Auth token","another app or adb run-as reads the token file",
              "Sandbox (UID separation) + Keystore-wrapped encryption" if "Keystore" in tok else "Sandbox only (token is plain text)",
              "Blocked" if "Keystore" in tok else ("Exposed" if app["allowBackup"] else "Partially Blocked"),"rooted device can still dump process memory" if "Keystore" in tok else "adb backup (allowBackup=true) extracts the plain-text token without root"))
    db=app["stores"]["appointments_db"]
    T.append(("T2","Information disclosure","Local DB","stolen device, file extraction",
              "File-based encryption + SQLCipher key in Keystore" if "Cipher" in db else "File-based encryption only","Blocked" if "Cipher" in db else "Partially Blocked","allowBackup=true lets the DB be copied by adb backup" if app["allowBackup"] else "key extraction on compromised OS"))
    api=app["network"][0]; ok=api["proto"]=="https"
    T.append(("T3","Tampering / Information disclosure","API traffic","network attacker (rogue Wi-Fi) reads or alters requests",
              "TLS 1.2+ with certificate pinning" if ok and api["pinning"] else ("TLS without pinning" if ok else "None (cleartext)"),
              "Blocked" if ok and api["pinning"] else ("Partially Blocked" if ok else "Exposed"),"pinned key rotation process" if ok and api["pinning"] else "rogue CA can intercept" if ok else "full read/modify of traffic"))
    an=app["network"][1]
    T.append(("T4","Information disclosure","Analytics traffic (device id)","passive sniffing of analytics host","None (HTTP)" if an["proto"]=="http" else "TLS","Exposed" if an["proto"]=="http" else "Blocked","device identifier leaves the device in clear text" if an["proto"]=="http" else "-"))
    rec=[c for c in app["components"] if c["name"]=="PatientRecordActivity"][0]
    T.append(("T5","Elevation of privilege","Exported activity (patient record)","adb shell am start / malicious app starts the screen directly",
              "exported=false (component visible only inside the app UID)" if not rec["exported"] else "none (exported=true, no permission)","Blocked" if not rec["exported"] else "Exposed","-" if not rec["exported"] else "any app can open the patient record screen"))
    sr=[c for c in app["components"] if c["name"]=="SyncReceiver"][0]
    T.append(("T6","Spoofing","Exported broadcast receiver","fake SYNC broadcast from another app","exported=true without a signature permission","Partially Blocked" if sr["exported"] and sr.get("permission") is None else "Blocked","forged broadcast can trigger sync and battery drain (no data read)"))
    T.append(("T7","Repudiation","Audit trail","user denies viewing a record","server-side signed audit log (outside this app)","Blocked","log integrity depends on the server"))
    T.append(("T8","Denial of service","Battery/CPU","hostile app floods the receiver","Doze/App Standby + sandbox cannot stop an exported receiver","Partially Blocked","rate limiting needed inside the receiver"))
    T.append(("T9","Spoofing","App package / update","repackaged APK installed","APK signature scheme v2 + Play protect + verified boot" if app["signed_v2"] else "none","Blocked" if app["signed_v2"] else "Exposed","side-loaded app with a different key is simply a different app"))
    T.append(("T10","Information disclosure","Location / camera","app reads sensors without consent","Runtime permissions (user grant at time of use)" if app["runtime_permission_requested_at_use"].get("CAMERA") else "install-time grant","Blocked","READ_CONTACTS is requested but the app never needs it (over-privilege)" if "READ_CONTACTS" in app["permissions"] else "-"))
    T.append(("T11","Information disclosure","debug_log on external storage","any app with storage access reads the log","none: external storage is not protected by the sandbox" if app["stores"]["debug_log"].startswith("external") else "private dir","Exposed" if app["stores"]["debug_log"].startswith("external") else "Blocked","may contain identifiers"))
    exposed=[t for t in T if t[5]=="Exposed"]; part=[t for t in T if t[5]=="Partially Blocked"]
    verdict="FAIL (do not release)" if exposed and any(t[2] in("Auth token","API traffic","Exported activity (patient record)") for t in exposed) else ("CONDITIONAL PASS (fix "+str(len(exposed))+" exposed items)" if exposed else "PASS with residual risks")
    return T,verdict
if __name__=="__main__":
    out={}
    for name in [None,"token_plain","export_record","cleartext"]:
        T,v=audit(APP,name); out[name or "baseline"]={"verdict":v,"rows":T}
        print("==",name or "baseline",v)
        for t in T: print(" ",t[0],t[2],"|",t[5])
    json.dump(out,open("../res_audit.json","w"),indent=1)
